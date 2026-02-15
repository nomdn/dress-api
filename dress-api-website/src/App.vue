<script setup>
        import { ref, reactive, onMounted, computed } from 'vue';
        import axios from 'axios';
        import Giscus from '@giscus/vue';
        import { Sunny, Moon, ArrowUp, ArrowDown } from '@element-plus/icons-vue';
        import { useDark, useToggle } from '@vueuse/core';
        import { ElCard, ElEmpty, ElButton, ElPagination, ElMenu, ElMenuItem } from 'element-plus';
        import { el } from 'element-plus/es/locales.mjs';

        const isDark = useDark();
        const activeIndex = ref('1');
        const toggleDark = useToggle(isDark);

        const title = ref("Dress API");
        const groupedImages = ref({});
        /* 这取决于你部署的API地址 */
        const remoteAPI = ref('https://dress.wsmdn.top/');
        const imgBaseURL = ref('https://fastly.jsdelivr.net/gh/Cute-Dress/Dress@master/');
        // 记录哪些作者被展开 { "Alice": true, "Bob": false }
        const expandedAuthors = reactive({});

        const loadJsonData = async () => {
                try {
                        const response = await axios.get('/index_1.json');
                        const data = response.data;
                        groupedImages.value = data;

                        // 初始化：全部折叠
                        for (const author in data) {
                                expandedAuthors[author] = false; // 默认展开，改成 false 就默认折叠
                        }
                } catch (err) {
                        console.error(err);
                        alert('加载数据失败: ' + err.message);
                }
        };

        const toggleExpand = (authorName) => {
                expandedAuthors[authorName] = !expandedAuthors[authorName];
        };

        const formatDate = (dateString) => {
                if (!dateString) return '未知时间';
                const date = new Date(dateString);
                return date.toLocaleDateString('zh-CN');
        };

        const handleImageError = (e) => {
                e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23000000"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="14" fill="%23F8F8FF">图片无法加载</text></svg>';
        };

        // 分页状态（每页显示多少个作者）
        const currentPage = ref(1);
        const pageSize = ref(10);

        // 计算总作者数（用于分页 total）
        const totalAuthors = computed(() => Object.keys(groupedImages.value).length);

        // 新增：判断当前作者是否在当前页
        const shouldShowAuthor = (index) => {
                const start = (currentPage.value - 1) * pageSize.value;
                const end = start + pageSize.value;
                return index >= start && index < end;
        };

        const handleSizeChange = (newSize) => {
                pageSize.value = newSize;
                currentPage.value = 1;
        };

        const handleCurrentChange = (newPage) => {
                currentPage.value = newPage;
        };

        const handleSelect = (key, keyPath) => {
                console.log('菜单选择:', key, keyPath);
        };

        axios.get(remoteAPI.value + "v1/health")
                .then(res => {
                        console.log('远程API响应:', res.data);
                        // 注意：axios自动解析JSON，不需要手动调用res.json()
                        const data = res.data;
                        console.log('远程API JSON数据:', data);
                        if (data.minimum_mode == "false") {
                                console.log('远程API正常，使用远程API地址加载图片');
                                imgBaseURL.value = remoteAPI.value + "img/";
                        } else {
                                const cdnURLs = [
                                        "https://cdn.jsdelivr.net/",
                                        "https://fastly.jsdelivr.net/",
                                        "https://gcore.jsdelivr.net/",
                                        "https://testingcf.jsdelivr.net/"
                                ];
                                for (const cdn of cdnURLs) {
                                        const testURL = cdn + "gh/Cute-Dress/Dress@master/README.md";
                                        axios.get(testURL)
                                                .then(() => {
                                                        imgBaseURL.value = cdn + "gh/Cute-Dress/Dress@master/";
                                                        console.log('使用CDN:', imgBaseURL.value);
                                                })
                                                .catch(() => {
                                                        console.warn('CDN不可用:', cdn);
                                                });
                                }
                        }
                })
                .catch(err => {
                        console.error('远程API请求失败:', err);
                        console.log("所以我们要用jsdelivr了喵");
                        const cdnURLs = [
                                "https://cdn.jsdelivr.net/",
                                "https://fastly.jsdelivr.net/",
                                "https://gcore.jsdelivr.net/",
                                "https://testingcf.jsdelivr.net/"
                        ];
                        for (const cdn of cdnURLs) {
                                const testURL = cdn + "gh/Cute-Dress/Dress@master/README.md";
                                axios.get(testURL)
                                        .then(() => {
                                                imgBaseURL.value = cdn + "gh/Cute-Dress/Dress@master/";
                                                console.log('使用CDN:', imgBaseURL.value);
                                        })
                                        .catch(() => {
                                                console.warn('CDN不可用:', cdn);
                                        });
                        }
                });

        onMounted(() => {
                loadJsonData();
        });
</script>

<template>
  <el-menu
      :default-active="activeIndex"
      mode="horizontal"
      :ellipsis="false"
      @select="handleSelect"
      
    >
    <el-menu-item index="0"><h3 style="width: max-content;">Dress-API</h3></el-menu-item>
    <el-menu-item index="1">
      <el-button type="primary" size="small"  @click="toggleDark()" v-if="isDark" :icon="Moon" round>Dark</el-button>
      <el-button type="primary" size="small"  @click="toggleDark()" v-else :icon="Sunny" round>Light</el-button>
    </el-menu-item>

  </el-menu>

  <div class="display-area">

    <h1>{{ title }}</h1>
    <h3>本项目图片资源来自<a href="https://github.com/Cute-Dress/Dress">Cute-Dress/Dress</a>,使用请遵守<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans">CC BY-NC-SA 4.0</a>协议！</h3>

    <!-- 按作者分组的可折叠卡片 -->
    <el-card 
      v-for="(author, authorName, index) in groupedImages" 
      :key="authorName"
      class="author-card"
      shadow="hover"
      v-show="shouldShowAuthor(index)"
    >
      <template #header>
        <div class="card-header" @click="toggleExpand(authorName)">
          <span style="font-weight: bold; font-size: 18px;">
            {{ authorName }} ({{ author.length }} 张图片)
          </span>
          <el-button 
            link 
            size="small"
            :icon="expandedAuthors[authorName] ? ArrowUp : ArrowDown"
          >
            {{ expandedAuthors[authorName] ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>

      <!-- 只在展开时渲染图片（懒加载） -->
      <div v-if="expandedAuthors[authorName]" class="image-grid">
        <div v-for="(image, idx) in author" :key="idx" class="image-card">
          <img 
            v-lazy="imgBaseURL + image.path" 
            :alt="image.path"
            @error="handleImageError"
            class="image-preview"
          />
          <div class="image-info">
            {{ formatDate(image.latest_commit_time) }}
          </div>
        </div>
      </div>
    </el-card>

    <el-empty 
      v-if="Object.keys(groupedImages).length === 0" 
      description="暂无数据"
      style="margin-top: 40px;"
    />
    <el-pagination
  v-model:page-size="pageSize"
  @size-change="handleSizeChange"
  @current-change="handleCurrentChange"
  :current-page="currentPage"
  :page-sizes="[5, 10, 20, 50]"
  :page-size="pageSize"
  layout="total, sizes, prev, pager, next, jumper"
  :total="totalAuthors">
  </el-pagination>

  <div class="giscus-area">
    <Giscus
      id="comments"
      repo="nomdn/dress-api"
      repo-id="R_kgDOQ9Pk4g"
      category="Announcements"
      category-id="DIC_kwDOQ9Pk4s4C2Z1w"
      mapping="title"
      strict="0"
      reactions-enabled="1"
      emit-metadata="0"
      input-position="top"
      theme="preferred_color_scheme"
      lang="zh-CN"
      loading="lazy"
    />
  </div>
  <a style="text-decoration:none;color:#51c4d3;margin-top: 10px;" href="https://travel.moe/go.html" title="异次元之旅-跃迁-我们一起去萌站成员的星球旅行吧！" target="_blank">
    <img src="https://travel.moe/images/icon/icon64.png" style="width:24px;height:24px">异次元之旅
  </a>

  <footer ><a href="https://github.com/nomdn/dress-api/">Dress-API</a> | <a href="https://github.com/Cute-Dress">Dress</a> | <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans">CC BY-NC-SA 4.0</a> | <a href="https://icp.gov.moe/?keyword=20260527" target="_blank">萌ICP备20260527号</a></footer>
  </div>
</template>

<style scoped>
@import './style.css';
.el-menu--horizontal {
  --el-menu-horizontal-height: 50px;
}
.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

</style>
