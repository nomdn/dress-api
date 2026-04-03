<script setup>
import { ref, onMounted, provide } from 'vue';
import axios from 'axios';

// 共享数据
const groupedImages = ref({});
const remoteAPI = ref('https://dress.wsmdn.top/');
const imgBaseURL = ref('https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress@master/');
const isLoading = ref(true);

// 提供数据给子组件
provide('groupedImages', groupedImages);
provide('remoteAPI', remoteAPI);
provide('imgBaseURL', imgBaseURL);
provide('isLoading', isLoading);

// 加载JSON数据
const loadJsonData = async () => {
  try {
    const response = await axios.get(remoteAPI.value + '/index_1.json');
    const data = response.data;
    groupedImages.value = data;
  } catch (err) {
    console.error(err);
    alert('加载数据失败: ' + err.message);
  } finally {
    isLoading.value = false;
  }
};

// 检查API健康状态
const checkApiHealth = async () => {
  try {
    const res = await axios.get(remoteAPI.value + "v1/health");
    console.log('远程API响应:', res.data);
    const data = res.data;
    console.log('远程API JSON数据:', data);
    if (data.minimum_mode == "false") {
      console.log('远程API正常，使用远程API地址加载图片');
      imgBaseURL.value = remoteAPI.value + "img/";
    } else {
      testCdnUrls();
    }
  } catch (err) {
    console.error('远程API请求失败:', err);
    console.log("所以我们要用jsdelivr了喵");
    testCdnUrls();
  } finally {
    // 无论API健康检查结果如何，都加载数据
    loadJsonData();
  }
};

// 测试CDN URLs
const testCdnUrls = () => {
  const cdnURLs = [
    "https://testingcf.jsdelivr.net/",
    "https://cdn.jsdelivr.net/",
    "https://fastly.jsdelivr.net/",
    "https://gcore.jsdelivr.net/"
  ];
  for (const cdn of cdnURLs) {
    const testURL = cdn + "gh/Cute-Dress/Dress@master/README.md";
    axios.get(testURL)
      .then(() => {
        imgBaseURL.value = cdn + "gh/Cute-Dress/Dress@master/";
        remoteAPI.value = cdn + "gh/nomdn/dress-api@main/";
        console.log('使用CDN:', imgBaseURL.value);
      })
      .catch(() => {
        console.warn('CDN不可用:', cdn);
      });
  }
};

// 页面挂载时请求API
onMounted(() => {
  checkApiHealth();
});
</script>

<template>
  <router-view />
      <footer>
      <a style="text-decoration:none;color:#e77c8e;margin-left: 20px;" href="https://travel.moe/go.html" title="异次元之旅-跃迁-我们一起去萌站成员的星球旅行吧！" target="_blank">
        <img src="https://travel.moe/images/icon/icon64pink.png" style="width:24px;height:24px">异次元之旅
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
@import "./style.css";
.some-link {
  display: flex;
  flex-direction: row;
  margin-left: 20px;
  margin-top: 5px;
}
</style>