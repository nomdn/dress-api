package main

import (
	"fmt"
	"log"
	"math/rand"
	"os"
	"sync"
	"time"

	"github.com/gin-contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/imroc/req/v3"
	"github.com/spf13/viper"
)

// ✅ 定义索引数据结构
type IndexEntry struct {
	Path   string `json:"path"`
	Time   string `json:"time"`
	Hash   string `json:"hash"`
	Author string `json:"author"`
}

type IndexData map[string]IndexEntry

// ✅ 全局存储索引数据
var (
	indexMutex sync.RWMutex
	indexData  IndexData
	miningMode bool
)

// ✅ 加载索引数据
func loadIndexData() error {
	log.Println("📥 正在获取远端索引...")

	client := req.C()

	var data IndexData
	resp, err := client.R().
		SetResult(&data).
		Get("https://testingcf.jsdelivr.net/gh/nomdn/dress-api@main/public/index_0.json")

	if err != nil {
		return fmt.Errorf("获取索引失败：%v", err)
	}

	if resp.StatusCode != 200 {
		return fmt.Errorf("HTTP 状态码：%d", resp.StatusCode)
	}

	// ✅ 线程安全更新
	indexMutex.Lock()
	indexData = data
	indexMutex.Unlock()

	log.Printf("✅ 索引加载成功，共 %d 条记录", len(data))
	return nil
}

// ✅ 获取随机图片
func getRandomDress() (IndexEntry, error) {
	indexMutex.RLock()
	defer indexMutex.RUnlock()

	if len(indexData) == 0 {
		return IndexEntry{}, fmt.Errorf("索引数据为空")
	}

	// ✅ 随机选择一个 Key
	keys := make([]string, 0, len(indexData))
	for k := range indexData {
		keys = append(keys, k)
	}

	rand.Seed(time.Now().UnixNano())
	randomKey := keys[rand.Intn(len(keys))]

	return indexData[randomKey], nil
}

func main() {
	// ✅ 1. 加载配置
	viper.SetConfigFile(".env")
	viper.SetDefault("PORTS", "8080")
	viper.SetDefault("MINING_MODE", "false")

	if err := viper.ReadInConfig(); err != nil {
		log.Printf("⚠️ .env 文件未找到：%v", err)
		log.Println("使用默认配置")
	} else {
		log.Printf("✅ 配置文件：%s", viper.ConfigFileUsed())
	}

	// ✅ 2. 检查运行模式
	if _, err := os.Stat("./Dress"); os.IsNotExist(err) {
		fmt.Println("⚠️ 目录不存在: ./Dress")
		fmt.Println("📦 使用最小化模式")
		miningMode = true
	} else {
		fmt.Println("✅ 目录存在: ./Dress")
		fmt.Println("📁 使用本地模式")
		miningMode = false
	}

	// ✅ 3. 加载索引数据（最小化模式必须）
	if miningMode {
		if err := loadIndexData(); err != nil {
			log.Fatalf("❌ 加载索引失败：%v", err)
		}
	}

	// ✅ 4. 初始化 Gin
	r := gin.Default()

	// ✅ 5. 注册路由
	r.GET("/v2/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":      "healthy",
			"mining_mode": miningMode,
			"index_count": len(indexData),
		})
	})

	r.GET("/v2/dress", func(c *gin.Context) {
		if miningMode {
			// ✅ 最小化模式：从内存获取
			entry, err := getRandomDress()
			if err != nil {
				c.JSON(500, gin.H{"error": err.Error()})
				return
			}

			c.JSON(200, gin.H{
				"img_url":     fmt.Sprintf("https://cdn.jsdelivr.net/gh/Cute-Dress/Dress@master/%s", entry.Path),
				"img_author":  entry.Author,
				"upload_time": entry.Time,
				"hash":        entry.Hash,
				"notice":      "Cute-Dress/Dress CC BY-NC-SA 4.0",
				"mode":        "minimum",
			})
		} else {
			// ✅ 本地模式：从本地读取
			indexMutex.RLock()
			data := indexData
			indexMutex.RUnlock()

			if len(data) == 0 {
				c.JSON(500, gin.H{"error": "索引数据为空"})
				return
			}

			keys := make([]string, 0, len(data))
			for k := range data {
				keys = append(keys, k)
			}

			rand.Seed(time.Now().UnixNano())
			randomKey := keys[rand.Intn(len(keys))]
			entry := data[randomKey]

			c.JSON(200, gin.H{
				"img_url":     fmt.Sprintf("/img/%s", entry.Path),
				"img_author":  entry.Author,
				"upload_time": entry.Time,
				"hash":        entry.Hash,
				"notice":      "Cute-Dress/Dress CC BY-NC-SA 4.0",
				"mode":        "local",
			})
		}
	})

	// ✅ 6. 静态文件
	r.Use(static.Serve("/", static.LocalFile("./public", false)))
	r.Use(static.Serve("/img", static.LocalFile("./Dress", false)))

	// ✅ 7. 启动服务器
	port := viper.GetString("PORTS")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 服务器启动在 :%s", port)
	log.Printf("📋 运行模式：%v", miningMode)
	log.Printf("📊 索引数据：%d 条", len(indexData))

	r.Run(":" + port)
}
