<script setup>
import { useRoute, useRouter } from 'vue-router';
import removeMd from 'remove-markdown';
import { Sunny, Moon, Loading } from '@element-plus/icons-vue';

import MarkdownIt from 'markdown-it';

import { generateSvgAvatar } from '../../../scripts/avatar_utils';

const route = useRoute();
const router = useRouter();
const navigateToHome = () => {
  router.push('/');
};
const authorname = route.params.authorname;

const isDark = useDark();
const toggleDark = useToggle(isDark);
const activeIndex = ref('1');

const groupedImages = useState('groupedImages');
const remoteAPI = useState('remoteAPI');
const imgBaseURL = useState('imgBaseURL');
const requestURL = useRequestURL();
const authorData = ref(null);
const markdownText = ref('');
const srcList = ref([]);
const readmeList=ref([])
const description = ref('');
const createSrcList = () => {
  if (authorData.value && authorData.value.contribution) {
    srcList.value = authorData.value.contribution.map(image => imgBaseURL.value + image.path);
  }
};
const loadAuthorData = async () => {
  try {
    // 1. 加载主数据
    const data = await $fetch(remoteAPI.value + 'index_1.json');
    groupedImages.value = data;
    console.log('主数据加载成功:', data);
    
    if (!groupedImages.value[authorname]) {
      console.warn(` 未找到作者: ${authorname}`);
      return;
    }
    
    authorData.value = groupedImages.value[authorname];
    
    // 2. 加载 README 文件（修复核心问题）
    if (authorData.value.readme?.length > 0) {
      // ✅ 清空旧数据，避免累加
      readmeList.value = [];
      console.log(authorData.value)
      
      console.log(`开始加载 ${authorData.value.readme.length} 个 README...`);
      
      // ✅ 方案：串行请求（稳，适合小数量，避免后端限流）
      for (const path of authorData.value.readme) {
        try {
          const res = await $fetch(imgBaseURL.value + path);
          readmeList.value.push(res);
          console.log(`加载成功: ${path}`);
        } catch (err) {
          console.error(`加载失败: ${path}`, err.message);
          // 可选：推入错误占位，保持顺序
          // readmeList.value.push(`<!-- 加载失败: ${path} -->`);
        }
        
      }
      description.value = markdownToPlainText(readmeList.value[0]);
      // ✅ 所有加载完成后，只打印一次最终结果
      console.log(`README 全部完成，共 ${readmeList.value.length} 项`);
      console.log(readmeList.value)

      // 🔍 调试用：查看真实数据（避免 Proxy 干扰）
      // console.log('📦 数据预览:', readmeList.value.slice(0, 3));
    }else {
      console.log('没有 README 文件，跳过加载');
      description.value = `${authorname} 的可爱照片喵~`;
    }
    
    // 3. ✅ 确保 README 加载完后再加载图片列表
    createSrcList();
    
  } catch (err) {
    console.error('❌ loadAuthorData 主流程异常:', err);
    if (import.meta.client) {
      alert('加载数据失败: ' + err.message);
    }
  }
};
const md = new MarkdownIt({
  html: false,       // 禁用原始 HTML 渲染，防止 XSS（外部 README 内容不可信）
  linkify: true,     // 自动将 URL 转为链接
  typographer: true, // 启用智能排版（如 "--" -> "—")
  breaks: true
});
function markdownToPlainText(mdText) {
  if (!mdText) return '';
  try {
    const text = removeMd(mdText);
    const cleanText = text.replace(/\n/g, " "); 
    return cleanText;
  } catch (err) {
    console.error('Markdown 转纯文本失败:', err);
    return mdText;
  }
}
// 在 setup 中创建计算属性
const renderedMarkdown = computed(() => {
  if (!markdownText.value) return '';
  return md.render(markdownText.value);
});

const formatDate = (dateString) => {
  if (!dateString) return '未知时间';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};


const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23000000"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="14" fill="%23F8F8FF">图片无法加载</text></svg>';
};

await loadAuthorData();
useHead({
  title: `${authorname} - Dress-API`,
  meta: [
    {
      name: 'description',
      content: description.value
    },
    {
      name: 'keywords',
      content: `${authorname}, Dress, Dress API, DressAPI, Dress API 文档, 女装,小男娘,可爱男孩子,小南梁,图灵派`
    },
    {
      name: 'og:title',
      content: `${authorname} - Dress-API`
    },
    {
      name: 'og:description',
      content: description.value.slice(0, 150) || `${authorname} 的可爱照片喵~`
    },
    {
      name: 'og:image',
      content: authorData.value?.avatar_url || null
    },
    {
      name: 'og:type',
      content: 'website'
    },
    {
      name: `og:url`,
      content: requestURL.href
    }

  ]
});

</script>

<template>
  <div class="app-container">
    <el-menu
      :default-active="activeIndex"
      mode="horizontal"
      :ellipsis="false"
    >
      <el-menu-item index="0">
        <el-icon @click="toggleDark()" v-if="isDark" style="cursor: pointer;"><Moon style="height: 20px; width: 20px;"/></el-icon>
        <el-icon @click="toggleDark()" v-else style="cursor: pointer;"><Sunny style="height: 20px; width: 20px;"/></el-icon>
        <h3 style="width: max-content; cursor: pointer;" @click="navigateToHome()">
          Dress-API
        </h3>
      </el-menu-item>
    </el-menu>

    <div class="display-area">
      <div v-if="authorData" class="author-detail">

        <!-- 作者头像和名字 -->
        <div class="author-header">
          <a v-if="authorData.github_username" :href="'https://github.com/'+authorData.github_username" target="_blank">
            <el-avatar shape="circle" size="large" fit="fill">
              <el-image :src="authorData.avatar_url" fit="fill" lazy :alt="authorname + ' 的头像'"></el-image>
            </el-avatar>
          </a>
          <a v-else href="https://github.com/404">
            <el-avatar shape="circle" size="large" fit="fill" :src="generateSvgAvatar(authorname)" :alt="authorname + ' 的头像'" loading="lazy"></el-avatar>
          </a>
          <h2>{{ authorname }}</h2>
        </div>

        <!-- Markdown 内容 -->
        <div v-for="text in readmeList" class="author-markdown" v-html="md.render(text)" style="text-align: left !important; margin: 20px 0;">
        </div>

        <!-- 图片卡片 -->
        <div class="author-images" v-if="authorData.contribution && authorData.contribution.length > 0">
          <div class="image-grid">
            <el-card 
              v-for="(image, index) in authorData.contribution" 
              :key="index"
              class="image-card"
              shadow="hover"
            >

              <el-image
                :src="imgBaseURL + image.path"
                :alt="authorname + ' 的图片 #' + (index + 1)"
                fit="cover"
                class="image-preview"
                @error="handleImageError"
                :preview-src-list="srcList"
                :initial-index="index"
              >
              <template #placeholder>
                <div class="image-header">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </template>
            </el-image>
              <div class="image-info">
                {{ formatDate(image.time) }}
              </div>
            </el-card>
          </div>
        </div>
      </div>

    </div>

  </div>
    <footer>
      <a style="text-decoration:none;color:#e77c8e;margin-left: 20px;" href="https://travel.moe/go.html" title="异次元之旅-跃迁-我们一起去萌站成员的星球旅行吧！" target="_blank">
        <img src="https://travel.moe/images/icon/icon64pink.png" alt="异次元之旅图标" style="width:24px;height:24px">异次元之旅
      </a>
      <div class="some-link"> 
        <a href="https://github.com/nomdn/dress-api/">Dress-API</a>&nbsp;&nbsp;
        <a href="https://github.com/Cute-Dress">Dress</a>&nbsp;&nbsp;
        <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans">CC BY-NC-SA 4.0</a>&nbsp;&nbsp;
        <a href="https://icp.gov.moe/?keyword=20260057" target="_blank">萌ICP备20260057号</a>&nbsp;&nbsp;
        <a href="https://beian.miit.gov.cn/" target="_blank">苏ICP备2026012471号</a>&nbsp;&nbsp;
      </div>
    </footer>
</template>

<style scoped>
@import '@/style.css';

/* 全局布局 */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  --el-color-primary: rgb(0, 0, 0);
}

html.dark .app-container {
  --el-color-primary: rgb(233, 233, 233);
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 50px;
  border-bottom: none !important;
  --el-menu-hover-bg-color: transparent !important;
  --el-menu-active-color: var(--el-text-color-primary) !important;
  --el-menu-bg-color: transparent !important;
}

.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}

/* 去除选中强调和下划线 */
.el-menu--horizontal > .el-menu-item.is-active {
  color: var(--el-text-color-primary) !important;
  background-color: transparent !important;
  border-bottom: none !important;
}

.el-menu--horizontal > .el-menu-item:hover {
  color: var(--el-text-color-primary) !important;
  background-color: transparent !important;
  border-bottom: none !important;
}

/* 去除所有可能的边框和下划线 */
.el-menu--horizontal::after {
  display: none !important;
}

.el-menu--horizontal > .el-menu-item {
  border-bottom: none !important;
  transition: none !important;
}

.el-menu--horizontal > .el-menu-item.is-active::after {
  display: none !important;
}

.el-icon {
  width: 40px;
  height: 40px;
  cursor: pointer;
}



/* 作者详情页面样式 */
.author-detail {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.author-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 40px 0;
}

.author-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.author-markdown {
  margin: 40px 0;
}

.author-images {
  margin: 40px 0;
  border-radius: 15px;
}

.author-images h3 {
  margin-bottom: 20px;
  font-size: 18px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.image-card {
  overflow: hidden;
  max-height: 280px;
  max-width: 300px;
}

.image-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.image-info {
  padding: 10px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.loading {
  text-align: center;
  margin: 100px 0;
  font-size: 18px;
  color: #909399;
}

/* 移动端安全区适配 */
@media screen and (max-width: 768px) {
  footer {
    padding-bottom: env(safe-area-inset-bottom);
  }
  
  .author-header {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .image-preview {
    height: 150px;
  }
}
</style>