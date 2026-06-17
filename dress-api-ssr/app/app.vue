<script setup>
import config from '../config/index';
// 共享数据

const remoteAPI = useState('remoteAPI', () => config.remote.remoteURL);
const imgBaseURL = useState('imgBaseURL', () => config.remote.imgURL);
const isLoading = ref(true);
const useLite = ref(config.useLite);
// ✅ 正确写法
const groupedImages = useState('groupedImages', () => ({}));

const loadJsonData = async () => {
  try {
    const { data, error } = await useFetch(remoteAPI.value + 'index_1.json');
    if (error.value) throw error.value;
    groupedImages.value = data.value;
  } catch (err) {
    console.error(err);
    useLite.value = true;
    try {
      const { data, error: rollbackError } = await useFetch(config.rollback.remoteURL + 'index_1.json');
      if (rollbackError.value) throw rollbackError.value;
      groupedImages.value = data.value;
      remoteAPI.value = config.rollback.remoteURL;
      imgBaseURL.value = config.rollback.imgURL;
    } catch (rollbackErr) {
      console.error('Rollback also failed:', rollbackErr);
    }
  } finally {
    isLoading.value = false;
  }
};
await loadJsonData();
onMounted(() => {
  useHead({
    script: [
        {
          defer: true,
          src: 'https://umami.wsmdn.top/sadfsdiq2.js',
          'data-website-id': '2598245e-f1e7-4fdd-a964-36c1d8e9edf2'
        },
      
      ]
  })
});
</script>

<template>
  <NuxtPage />

</template>

<style scoped>
@import "@/style.css";

</style>