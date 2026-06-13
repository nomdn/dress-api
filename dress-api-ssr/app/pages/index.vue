<script setup>
import { useRouter } from 'vue-router';

import { generateSvgAvatar } from '../scripts/avatar_utils.js';
import { Sunny, Moon, Search } from '@element-plus/icons-vue';
import { useDark, useToggle } from '@vueuse/core';
import config from '~~/config/index.js';



const router = useRouter();

const navigateToAuthor = (authorName) => {
  router.push(`/author/${authorName}`);
};

const visible = ref(false);
const isDark = useDark();
const activeIndex = ref('1');
const toggleDark = useToggle(isDark);
const searchQuery = ref('');
const requestURL = useRequestURL();
// 从App.vue注入共享数据
const groupedImages = useState('groupedImages');


const filteredAuthors = computed(() => {
  if (!groupedImages.value) return [];
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) {
    return Object.keys(groupedImages.value);
  }
  return Object.keys(groupedImages.value).filter(authorName => 
    authorName.toLowerCase().includes(query)
  );
});

const currentPage = ref(1);
const pageSize = ref(20);

const totalAuthors = computed(() => filteredAuthors.value.length);

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

watch(searchQuery, () => {
  currentPage.value = 1;
});

const isNarrow = ref(false);
let mediaQueryList = null;
const paginationModules = () =>{
  if (!isNarrow.value) {
    return "total, sizes, prev, pager, next, jumper";
  }else{
    return "sizes,pager, prev, next";
  }
}
onMounted(() => {
  mediaQueryList = window.matchMedia('(max-width: 768px)');
  isNarrow.value = mediaQueryList.matches;
  
  // 监听窗口大小变化（可选，增强体验）
  const handler = (e) => {
    isNarrow.value = e.matches;
    visible.value = false; // 窗口大小变化时关闭搜索框
  };
  mediaQueryList.addEventListener('change', handler);

  // 清理监听器
  onBeforeUnmount(() => {
    mediaQueryList.removeEventListener('change', handler);
  });

  console.log("当前设备是否是窄屏：" + isNarrow.value);
});
useHead({
  title: 'Dress API - 面向可爱男孩子的前端 | 随机图API Dress API前端',
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: 'Dress API',
        url: config.siteUrl,
        description: 'Dress API是一个面向可爱男孩子的图片分享平台，基于Dress项目提供随机图片API服务。',
        publisher: {
          '@type': 'Organization',
          name: 'Dress API Team',
        },
      }),
    },
  ],
  meta: [
    {
      name: 'description',
      content: 'Dress API是一个面向可爱男孩子的图片分享平台，基于Dress项目提供随机图片API服务。浏览海量图片作品、查看图片作者信息与版权声明，支持暗色模式与响应式布局，为程序猿和图片爱好者打造的前端站点。'
    },
    {
      name: 'keywords',
      content: 'Dress API, DressAPI, 可爱男孩子, 图片分享, 随机图片API, 图灵派, 程序员, MTF, dress图库, 图片作者'
    },
    {
      name: 'author',
      content: 'Dress API Team, nomdn'
    },
    {
      name: 'robots',
      content: 'index, follow'
    },
    {
      name: 'theme-color',
      content: '#242424'
    },
    {
      property: 'og:title',
      content: 'Dress API - 面向可爱男孩子的前端 | 随机图片API前端'
    },
    {
      property: 'og:description',
      content: 'Dress API是一个面向可爱男孩子的图片分享平台，基于Dress项目提供随机图片API服务。浏览海量图片作品、查看图片作者信息与版权声明。'
    },
    {
      property: 'og:image',
      content: config.siteUrl + 'favicon.png'
    },
    {
      property: 'og:type',
      content: 'website'
    },
    {
      property: 'og:url',
      content: requestURL.href
    },
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
        <h3 style="width: max-content;">Dress-API</h3>
      </el-menu-item>
      <el-menu-item index="2">
        <span v-if="searchQuery" style="margin-left: 10px;">
          找到 {{ filteredAuthors.length }} 位作者
        </span>
      </el-menu-item>
      <el-menu-item index="1">
        <div class="search-container"> 
          <el-input
            v-if="!isNarrow"
            v-model="searchQuery"
            placeholder="搜索作者..."
            style="width: 100%;"
            clearable
            size="large"
            :prefix-icon="Search"
          />
        </div>

          <el-popover
        :visible="visible"
        placement="bottom"
        :width="200"
        v-if="isNarrow"
        >
          <el-input
            v-model="searchQuery"
            placeholder="搜索作者..."
            clearable
            size="large"
            :prefix-icon="Search"
          />
          <template #reference>
            <el-icon v-if="isNarrow" class="menu-icon" @click="visible = !visible" >
              <Search />
            </el-icon>
          </template>
        </el-popover>

      </el-menu-item>

    </el-menu>

    <h1 class="seo-heading">Dress API - 可爱男孩子图片分享平台</h1>
    <div class="display-area">
      <!-- 按作者分组的可折叠卡片 -->
      <RouterLink 
      v-for="(authorName, index) in filteredAuthors" 
      :key="authorName"
      :to="'/author/'+authorName"
      class="author-link"
      >
        <el-card 
        class="author-card"
        shadow="hover"
        v-show="shouldShowAuthor(index)"
        @click="navigateToAuthor(authorName)"
        style="cursor: pointer;"
      >

          <div class="card-header">
            
              <el-avatar shape="circle" size="large" fit="fill" v-if="groupedImages[authorName]?.github_username" @click="'https://github.com/'+groupedImages[authorName].github_username" style="cursor: pointer;">
                <el-image :src="groupedImages[authorName].avatar_url" fit="fill" lazy :alt="authorName + ' 的头像'"></el-image>
              </el-avatar>

              <el-avatar shape="circle" size="large" fit="fill" :src="generateSvgAvatar(authorName)" :alt="authorName + ' 的头像'" loading="lazy" v-else ></el-avatar>
            <span style="font-weight: bold; font-size: 18px;">
              {{ authorName }}
            </span>
          </div>
      </el-card>
      </RouterLink>

    </div>


  </div>
      <div class="pagination-container">
        <el-pagination
          v-if = "filteredAuthors.length>0"
          v-model:page-size="pageSize"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[20, 40, 60,80]"
          :page-size="pageSize"
          :layout="paginationModules()"
          :total="totalAuthors"
          :small="isNarrow"
        >
        </el-pagination>
      </div>
      <footer>
      <a style="text-decoration:none;color:#e77c8e;margin-left: 20px;" href="https://travel.moe/go.html" title="异次元之旅-跃迁-我们一起去萌站成员的星球旅行吧！" target="_blank">
        <img src="https://travel.moe/images/icon/icon64pink.png" alt="异次元之旅图标" style="width:24px;height:24px;">异次元之旅
      </a>
      <div class="some-link"> 
        <a href="https://github.com/nomdn/dress-api/">Dress-API</a>&nbsp&nbsp
        <a href="https://github.com/Cute-Dress">Dress</a>&nbsp&nbsp
        <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans">CC BY-NC-SA 4.0</a>&nbsp&nbsp
        <a href="https://icp.gov.moe/?keyword=20260057" target="_blank">萌ICP备20260057号</a>&nbsp&nbsp
      </div>
    </footer>
</template>

<style scoped>

@import '@/style.css';
/* SEO标题：视觉隐藏但对搜索引擎和屏幕阅读器可见 */
.seo-heading {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 全局布局 */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  --el-color-primary: #313131;
}

html.dark .app-container {
  --el-color-primary: rgb(233, 233, 233);
}

.el-button {
  background-color: transparent;
  color: var(--el-color-primary);
  border: 1px solid transparent;
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

/* 去除 input 组件的选择强调并固定宽度 */
.search-container .el-input {
  max-width: 300px !important;
  width: 300px !important;
}

.el-input__wrapper {
  box-shadow: none !important;
  border-color: var(--el-border-color) !important;
}

.el-input__wrapper.is-focus {
  box-shadow: none !important;
  border-color: var(--el-border-color) !important;
}

.el-input__wrapper:hover {
  box-shadow: none !important;
  border-color: var(--el-border-color) !important;
}

.el-icon {
  width: 40px;
  height: 40px;
  cursor: pointer;
}
.pagination-container {
  margin: 0 auto;
  margin-top: 20px;
  max-width: 10px;
}


/* 移动端安全区适配 */
@media screen and (max-width: 768px) {
  footer {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>
<style>

:root {
  --el-color-primary: #313131; /* 黑色 */
}
html.dark {
  --el-color-primary: #e9e9e9; /* 暗色模式 */
}
</style>