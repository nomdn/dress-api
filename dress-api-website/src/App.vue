<script setup>
import { ref, onMounted, provide } from 'vue';
import axios from 'axios';
import config from './config/index';

// 共享数据
const groupedImages = ref({});
const remoteAPI = ref('https://dress.wsmdn.top/');
const imgBaseURL = ref('https://testingcf.jsdelivr.net/gh/Cute-Dress/Dress@master/');
const isLoading = ref(true);
const useMinimum = ref(config.useMinimum);
if (config.remote.remoteURL) {
  remoteAPI.value = config.remote.remoteURL;
}
if (config.remote.imgBaseURL) {
  imgBaseURL.value = config.remote.imgBaseURL;
}

// 提供数据给子组件
provide('groupedImages', groupedImages);
provide('remoteAPI', remoteAPI);
provide('imgBaseURL', imgBaseURL);
provide('isLoading', isLoading);

// 加载JSON数据
const loadJsonData = async () => {
  try {
    const response = await axios.get(remoteAPI.value + 'index_1.json');
    const data = response.data;
    groupedImages.value = data;
  } catch (err) {
    console.error(err);
    useMinimum.value = true; // 切换到最小模式
    loadJsonData();
    
  } finally {
    isLoading.value = false;
  }
};

// 检查API健康状态
const checkApiHealth = async () => {
  try {
    if (useMinimum.value == false) {
      console.log('使用远程API地址加载图片');
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
    "https://testingcf.jsdelivr.net/"
  ];
  for (const cdn of cdnURLs) {
    const testURL = cdn + "gh/Cute-Dress/Dress@master/README.md";
    axios.get(testURL)
      .then(() => {
        imgBaseURL.value = cdn + "gh/Cute-Dress/Dress@master/";
        remoteAPI.value = cdn + "gh/nomdn/dress-api@main/public/";
        console.log('使用CDN:', imgBaseURL.value);
        return; // 成功后停止测试其他CDN
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

</template>

<style scoped>
@import "./style.css";

</style>