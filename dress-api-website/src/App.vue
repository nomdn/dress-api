<script setup>
import { ref, onMounted, provide } from 'vue';
import axios from 'axios';
import config from './config/index';

// 共享数据
const groupedImages = ref({});
const remoteAPI = ref(config.remote.remoteURL);
const imgBaseURL = ref(config.remote.imgURL);
const isLoading = ref(true);
const useLite = ref(config.useLite);

provide('groupedImages', groupedImages);
provide('remoteAPI', remoteAPI);
provide('imgBaseURL', imgBaseURL);
provide('isLoading', isLoading);

const loadJsonData = async () => {
  try {
    const response = await axios.get(remoteAPI.value + 'index_1.json');
    groupedImages.value = response.data;
  } catch (err) {
    console.error(err);
    useLite.value = true;
    const response = await axios.get(config.rollback.remoteURL + 'index_1.json');
    groupedImages.value = response.data;
    remoteAPI.value = config.rollback.remoteURL;
    imgBaseURL.value = config.rollback.imgURL;
  } finally {
    isLoading.value = false;
  }
};

onMounted(loadJsonData);
</script>

<template>
  <router-view />

</template>

<style scoped>
@import "./style.css";

</style>