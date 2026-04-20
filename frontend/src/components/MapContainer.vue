<script setup>
import { onMounted, onUnmounted, ref, defineExpose } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";

const props = defineProps({
  height: {
    type: String,
    default: "460px"
  }
});

const emit = defineEmits(["ready"]);

const map = ref(null)

defineExpose({
  map
})


onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: "7a3bc01057bbcf9fead210b293e40228",
  };
  AMapLoader.load({
    key: "5c2d03efdd5e67fe3b928f80f6a384f0", // 申请好的Web端开发者Key，首次调用 load 时必填
    version: "2.0", // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
    plugins: ["AMap.Scale"], //需要使用的的插件列表，如比例尺'AMap.Scale'，支持添加多个如：['...','...']
  })
      .then((AMap) => {
        map.value = new AMap.Map("container", {
          // 设置地图容器id
          // viewMode: "3D", // 是否为3D地图模式
          zoom: 11, // 初始化地图级别
          center: [116.397428, 39.90923], // 初始化地图中心点位置
        });
        emit("ready", { map: map.value, AMap });
      })
      .catch((e) => {
        console.log(e);
      });
});

onUnmounted(() => {
  map.value?.destroy();
});
</script>

<template>
  <div id="container" :style="{ height: props.height }"></div>
</template>

<style scoped>
#container {
  width: 100%;
}
</style>
