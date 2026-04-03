<script setup>
import { ref, computed, watch, inject } from 'vue';
import { useRouter } from 'vue-router';
import { generateSvgAvatar } from '../scripts/avatar_utils.js';
import { Sunny, Moon, Search } from '@element-plus/icons-vue';
import { useDark, useToggle } from '@vueuse/core';
import { ElCard, ElEmpty, ElPagination, ElMenu, ElMenuItem, ElAvatar, ElImage, ElInput } from 'element-plus';

const router = useRouter();

const navigateToAuthor = (authorName) => {
  router.push(`/author/${authorName}`);
};

const isDark = useDark();
const activeIndex = ref('1');
const toggleDark = useToggle(isDark);
const searchQuery = ref('');

// 从App.vue注入共享数据
const groupedImages = inject('groupedImages');
const remoteAPI = inject('remoteAPI');
const imgBaseURL = inject('imgBaseURL');
const isLoading = inject('isLoading');

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
</script>

<template>
  <div class="app-container">
    <el-menu
      :default-active="activeIndex"
      mode="horizontal"
      :ellipsis="false"
      @select="handleSelect"
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
        <el-input
          v-model="searchQuery"
          placeholder="搜索作者..."
          sytle="width: 100%;"
          clearable
          size="large"
          :prefix-icon="Search"
          
        />
      </el-menu-item>
    </el-menu>

    <div class="display-area">
      <!-- 按作者分组的可折叠卡片 -->
      <el-card 
        v-for="(authorName, index) in filteredAuthors" 
        :key="authorName"
        class="author-card"
        shadow="hover"
        v-show="shouldShowAuthor(index)"
      >
        <div class="card-header" @click="navigateToAuthor(authorName)">
          <a v-if="groupedImages[authorName].github_username" :href="'https://github.com/'+groupedImages[authorName].github_username" target="_blank">
            <el-avatar shape="circle" size="large" fit="fill">
              <el-image :src="groupedImages[authorName].avatar_url" fit="fill" lazy></el-image>
            </el-avatar>
          </a>
          <a v-else href="https://github.com/404">
            <el-avatar shape="circle" size="large" fit="fill" :src="generateSvgAvatar(authorName)" loading="lazy"></el-avatar>
          </a>
          <span style="font-weight: bold; font-size: 18px;">
            {{ authorName }}
          </span>
        </div>
      </el-card>

    </div>


  </div>
        <div style="width: 80%;max-width: 1000px;margin-bottom: 20px;margin: 0 auto;">
        <el-pagination
          v-if = "filteredAuthors.length>0"
          v-model:page-size="pageSize"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[20, 40, 60,80]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalAuthors"
        >
        </el-pagination>
      </div>
</template>

<style scoped>
@import '../style.css';

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
.el-input {
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



/* 移动端安全区适配 */
@media screen and (max-width: 768px) {
  footer {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>