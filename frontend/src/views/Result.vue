<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Calendar, Download, Location, Money, RefreshRight, Sunny, Tickets } from "@element-plus/icons-vue";
import MapContainer from "@/components/MapContainer.vue";
import { getAttractionPhotos } from "@/services/api.js";

const router = useRouter();

const rawTripPlan = ref(null);
const parseError = ref("");
const activeDayIndex = ref(0);

const mapInstance = ref(null);
const aMapInstance = ref(null);
const markerRefs = ref([]);
const photoMap = ref({});
const photoLoadingMap = ref({});
const photoErrorMap = ref({});

const normalizeArray = (value) => (Array.isArray(value) ? value : []);

const unwrapTripPlanPayload = (payload) => {
  if (!payload || typeof payload !== "object") return null;

  if (payload?.data?.result && typeof payload.data.result === "object") {
    return payload.data.result;
  }

  if (payload?.result && typeof payload.result === "object") {
    return payload.result;
  }

  if (payload?.data && typeof payload.data === "object" && !Array.isArray(payload.data)) {
    return payload.data;
  }

  return payload;
};

const budgetLabelMap = {
  attraction_budget: "景点预算",
  hotel_budget: "酒店预算",
  meal_budget: "餐饮预算",
  total_budget: "总预算",
  transportation_budget: "交通预算"
};

const mealTypeLabelMap = {
  breakfast: "早餐",
  lunch: "午餐",
  dinner: "晚餐"
};

const onMapReady = ({ map, AMap }) => {
  mapInstance.value = map;
  aMapInstance.value = AMap;
  syncMarkers();
};

const toNumber = (value) => {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
};

const getAttractions = (day) => {
  if (!day || typeof day !== "object") return [];
  return Array.isArray(day.attraction) ? day.attraction : Array.isArray(day.attractions) ? day.attractions : [];
};

const getPhotoKey = (attraction) => {
  const city = (tripPlan.value?.city || "").trim().toLowerCase();
  const name = (attraction?.name || "").trim().toLowerCase();
  return `${city}::${name}`;
};

const getPhotoUrlFromResponse = (item) => {
  return item?.url || item?.urls?.regular || item?.urls?.small || "";
};

const normalizeTripPlan = (plan) => {
  if (!plan || typeof plan !== "object") return null;

  const days = normalizeArray(plan.days).map((day, dayIndex) => {
    const attractions = getAttractions(day).map((item) => {
      const longitude = toNumber(item?.location?.longitude ?? item?.longitude);
      const latitude = toNumber(item?.location?.latitude ?? item?.latitude);

      return {
        name: item?.name || "未命名景点",
        description: item?.description || item?.intro || "暂无介绍",
        category: item?.category || "",
        rating: item?.rating ?? null,
        ticketPrice: item?.ticket_price ?? item?.ticketPrice ?? null,
        visitDuration: item?.visit_duration ?? item?.visitDuration ?? null,
        longitude,
        latitude,
        address: item?.address || "",
        imageUrl: item?.image_url || item?.imageUrl || ""
      };
    });

    const hotel = day?.hotel && typeof day.hotel === "object"
      ? {
          name: day.hotel.name || day.accommodation || "暂无酒店信息",
          address: day.hotel.address || "",
          cost: day.hotel.cost ?? null,
          distance: day.hotel.distance || "",
          priceRange: day.hotel.price_range || day.hotel.priceRange || "",
          rating: day.hotel.rating ?? null,
          longitude: toNumber(day.hotel?.location?.longitude),
          latitude: toNumber(day.hotel?.location?.latitude)
        }
      : null;

    const meals = normalizeArray(day?.meals).map((item) => ({
      name: item?.name || "未命名餐饮",
      type: item?.type || "",
      cost: item?.cost ?? null,
      description: item?.description || "",
      address: item?.address || ""
    }));

    return {
      title: day?.title || day?.day_title || `第 ${dayIndex + 1} 天`,
      date: day?.date || day?.day_date || "",
      description: day?.description || day?.suggestion || day?.tips || "",
      accommodation: day?.accommodation || hotel?.name || "",
      hotel,
      meals,
      transportation: day?.transportation ?? null,
      attractions
    };
  });

  const budget = plan.budget && typeof plan.budget === "object" ? plan.budget : null;

  return {
    city: plan.city || "目的地",
    startDate: plan.start_date || "",
    endDate: plan.end_date || "",
    overallSuggestion: plan.overall_suggestion || "暂无总体建议",
    days,
    weather: normalizeArray(plan.weather_condition),
    budget
  };
};

const tripPlan = computed(() => normalizeTripPlan(rawTripPlan.value));
const hasTripData = computed(() => !!tripPlan.value && tripPlan.value.days.length > 0);

const selectedDay = computed(() => {
  if (!tripPlan.value?.days?.length) return null;
  return tripPlan.value.days[activeDayIndex.value] || tripPlan.value.days[0];
});

const weatherCards = computed(() => {
  return (tripPlan.value?.weather || []).map((item, index) => ({
    date: item?.date || item?.day || `第 ${index + 1} 天`,
    dayWeather: item?.day_weather || item?.condition || item?.weather || "天气待更新",
    nightWeather: item?.night_weather || "",
    dayTemperature: item?.day_temperature ?? item?.temperature ?? null,
    nightTemperature: item?.night_temperature ?? null,
    windDirection: item?.wind_direction || item?.wind || "",
    windPower: item?.wind_power || item?.wind_level || ""
  }));
});

const budgetEntries = computed(() => {
  const budget = tripPlan.value?.budget;
  if (!budget) return [];
  return Object.entries(budget).map(([key, value]) => ({
    key,
    label: budgetLabelMap[key] || key,
    value: value ?? "-"
  }));
});

const loadTripPlan = () => {
  // 为了调试，先改为从 localStorage 获取数据，正式环境可以切回 sessionStorage
  // const data = sessionStorage.getItem("tripPlan");

  const data = localStorage.getItem("tripPlan");

  if (!data) {
    parseError.value = "未找到行程数据，请返回首页重新生成。";
    return;
  }

  try {
    rawTripPlan.value = unwrapTripPlanPayload(JSON.parse(data));
    parseError.value = "";
  } catch (error) {
    rawTripPlan.value = null;
    parseError.value = "行程数据解析失败，请重新生成。";
    ElMessage.error(`解析失败: ${error?.message || "未知错误"}`);
  }
};

const getAttractionPhotoUrl = (attraction) => {
  if (attraction?.imageUrl) return attraction.imageUrl;
  const key = getPhotoKey(attraction);
  return photoMap.value[key] || "";
};

const isAttractionPhotoLoading = (attraction) => {
  const key = getPhotoKey(attraction);
  return !!photoLoadingMap.value[key];
};

const isAttractionPhotoError = (attraction) => {
  const key = getPhotoKey(attraction);
  return !!photoErrorMap.value[key];
};

const fetchAttractionPhoto = async (attraction) => {
  const key = getPhotoKey(attraction);
  const attractionName = attraction?.name?.trim();
  if (!key || !attractionName || attraction?.imageUrl || photoMap.value[key] || photoLoadingMap.value[key]) return;

  photoLoadingMap.value = { ...photoLoadingMap.value, [key]: true };
  photoErrorMap.value = { ...photoErrorMap.value, [key]: false };

  try {
    const photos = await getAttractionPhotos(attractionName);
    const photoUrl = (Array.isArray(photos) ? photos : []).map(getPhotoUrlFromResponse).find(Boolean) || "";
    if (photoUrl) {
      photoMap.value = { ...photoMap.value, [key]: photoUrl };
    } else {
      photoErrorMap.value = { ...photoErrorMap.value, [key]: true };
    }
  } catch {
    photoErrorMap.value = { ...photoErrorMap.value, [key]: true };
  } finally {
    photoLoadingMap.value = { ...photoLoadingMap.value, [key]: false };
  }
};

const prefetchAttractionPhotos = async (attractions) => {
  const uniqueAttractions = [];
  const seen = new Set();

  (Array.isArray(attractions) ? attractions : []).forEach((item) => {
    const key = getPhotoKey(item);
    if (!key || seen.has(key)) return;
    seen.add(key);
    uniqueAttractions.push(item);
  });

  await Promise.allSettled(uniqueAttractions.map((item) => fetchAttractionPhoto(item)));
};

const retryFetchAttractionPhoto = (attraction) => {
  const key = getPhotoKey(attraction);
  if (!key) return;
  photoErrorMap.value = { ...photoErrorMap.value, [key]: false };
  void fetchAttractionPhoto(attraction);
};

const clearMarkers = () => {
  if (!mapInstance.value || !markerRefs.value.length) return;
  mapInstance.value.remove(markerRefs.value);
  markerRefs.value = [];
};

const syncMarkers = () => {
  if (!mapInstance.value || !aMapInstance.value) return;

  clearMarkers();

  const attractions = selectedDay.value?.attractions || [];
  const validAttractions = attractions.filter((item) => item.longitude !== null && item.latitude !== null);
  if (!validAttractions.length) return;

  markerRefs.value = validAttractions.map((item, index) => {
    return new aMapInstance.value.Marker({
      position: [item.longitude, item.latitude],
      title: item.name,
      label: {
        content: `${index + 1}`,
        direction: "top"
      }
    });
  });

  mapInstance.value.add(markerRefs.value);
  mapInstance.value.setFitView(markerRefs.value, false, [80, 80, 80, 80]);
};

const focusAttraction = (item) => {
  if (!mapInstance.value || item.longitude === null || item.latitude === null) return;
  mapInstance.value.setZoomAndCenter(14, [item.longitude, item.latitude]);
};

const goHome = () => {
  router.push("/");
};

const sanitizeFileName = (value) => {
  return (value || "trip-plan").replace(/[\\/:*?"<>|]/g, "-").trim();
};

const buildExportContent = () => {
  const plan = tripPlan.value;
  if (!plan) return "";

  const lines = [
    `# ${plan.city} 行程推荐`,
    "",
    `- 日期: ${plan.startDate || "-"} 至 ${plan.endDate || "-"}`,
    "",
    "## 总体建议",
    plan.overallSuggestion || "暂无总体建议",
    ""
  ];

  lines.push("## 预算参考");
  if (budgetEntries.value.length) {
    budgetEntries.value.forEach((item) => {
      lines.push(`- ${item.label}: ${item.value}`);
    });
  } else {
    lines.push("- 暂无预算信息");
  }

  lines.push("", "## 天气概览");
  if (weatherCards.value.length) {
    weatherCards.value.forEach((item) => {
      lines.push(
        `- ${item.date}: 白天 ${item.dayWeather}${item.dayTemperature !== null ? `, ${item.dayTemperature}°C` : ""}${item.nightWeather ? `；夜间 ${item.nightWeather}` : ""}${item.nightTemperature !== null ? `, ${item.nightTemperature}°C` : ""}${item.windDirection ? `；${item.windDirection}` : ""}${item.windPower ? `, ${item.windPower}` : ""}`
      );
    });
  } else {
    lines.push("- 暂无天气信息");
  }

  lines.push("", "## 每日行程");
  plan.days.forEach((day, dayIndex) => {
    lines.push(`### Day ${dayIndex + 1} ${day.title || ""}`.trim());
    if (day.date) lines.push(`- 日期: ${day.date}`);
    if (day.description) lines.push(`- 说明: ${day.description}`);
    if (day.accommodation) lines.push(`- 住宿: ${day.accommodation}`);
    if (day.hotel?.name) lines.push(`- 酒店: ${day.hotel.name}${day.hotel.cost !== null ? `（约 ${day.hotel.cost}）` : ""}`);
    if (day.transportation !== null && day.transportation !== undefined) lines.push(`- 交通: ${day.transportation}`);
    if (day.meals.length) {
      lines.push("- 餐饮:");
      day.meals.forEach((item) => {
        lines.push(`  - ${mealTypeLabelMap[item.type] || item.type || "餐饮"}: ${item.name}${item.cost !== null ? `（${item.cost}）` : ""}`);
      });
    }
    if (day.attractions.length) {
      day.attractions.forEach((item, index) => {
        lines.push(`- ${index + 1}. ${item.name}${item.address ? ` (${item.address})` : ""}`);
        if (item.description) lines.push(`  - ${item.description}`);
      });
    } else {
      lines.push("- 暂无景点安排");
    }
    lines.push("");
  });

  return lines.join("\n");
};

const exportTripPlan = () => {
  if (!hasTripData.value) {
    ElMessage.warning(parseError.value || "暂无可导出的行程数据");
    return;
  }

  const content = buildExportContent();
  if (!content) {
    ElMessage.warning("导出内容为空");
    return;
  }

  const fileName = sanitizeFileName(`${tripPlan.value.city}-${tripPlan.value.startDate}-${tripPlan.value.endDate}.md`);
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  ElMessage.success("行程已导出为 Markdown");
};

watch(
  () => tripPlan.value?.days?.length,
  (len) => {
    if (!len) return;
    if (activeDayIndex.value >= len) activeDayIndex.value = 0;
  }
);

watch(
  () => [activeDayIndex.value, selectedDay.value?.attractions?.length, mapInstance.value],
  () => {
    syncMarkers();
  }
);

const selectedDayHasCoordinates = computed(() => {
  return (selectedDay.value?.attractions || []).some((item) => item.longitude !== null && item.latitude !== null);
});

watch(
  () => selectedDay.value?.attractions,
  (attractions) => {
    void prefetchAttractionPhotos(attractions || []);
  },
  { immediate: true }
);

onMounted(() => {
  loadTripPlan();
});
</script>

<template>
  <div class="result-page">
    <el-card v-if="hasTripData" class="result-card" shadow="never">
      <div class="header-row">
        <div>
          <h2>{{ tripPlan.city }} 行程推荐</h2>
          <p>
            <el-icon><Calendar /></el-icon>
            {{ tripPlan.startDate }} - {{ tripPlan.endDate }}
          </p>
        </div>
        <div class="header-actions">
          <el-button type="primary" plain @click="exportTripPlan">
            <el-icon><Download /></el-icon>
            导出行程
          </el-button>
          <el-button plain @click="goHome">
            <el-icon><RefreshRight /></el-icon>
            重新生成
          </el-button>
        </div>
      </div>

      <el-row :gutter="16" class="meta-row">
        <el-col :xs="24" :md="12">
          <el-card class="panel" shadow="hover">
            <template #header>
              <div class="panel-title">
                <el-icon><Tickets /></el-icon>
                <span>总体建议</span>
              </div>
            </template>
            <p class="overall-text">{{ tripPlan.overallSuggestion }}</p>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="6">
          <el-card class="panel" shadow="hover">
            <template #header>
              <div class="panel-title">
                <el-icon><Money /></el-icon>
                <span>预算参考</span>
              </div>
            </template>
            <div v-if="budgetEntries.length" class="budget-list">
              <div v-for="item in budgetEntries" :key="item.key" class="budget-item">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <el-empty v-else description="暂无预算信息" :image-size="80" />
          </el-card>
        </el-col>

        <el-col :xs="24" :md="6">
          <el-card class="panel" shadow="hover">
            <template #header>
              <div class="panel-title">
                <el-icon><Location /></el-icon>
                <span>行程概览</span>
              </div>
            </template>
            <div class="overview-list">
              <div class="overview-item">
                <span>城市</span>
                <strong>{{ tripPlan.city }}</strong>
              </div>
              <div class="overview-item">
                <span>日期</span>
                <strong>{{ tripPlan.startDate }} - {{ tripPlan.endDate }}</strong>
              </div>
              <div class="overview-item">
                <span>天数</span>
                <strong>{{ tripPlan.days.length }} 天</strong>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="panel" shadow="hover">
        <template #header>
          <div class="panel-title">
            <el-icon><Sunny /></el-icon>
            <span>天气概览</span>
          </div>
        </template>
        <el-empty v-if="!weatherCards.length" description="暂无天气信息" :image-size="80" />
        <div v-else class="weather-grid">
          <div v-for="item in weatherCards" :key="item.date" class="weather-item">
            <h4>{{ item.date }}</h4>
            <p><strong>白天：</strong>{{ item.dayWeather }}<span v-if="item.dayTemperature !== null">（{{ item.dayTemperature }}°C）</span></p>
            <p v-if="item.nightWeather"><strong>夜间：</strong>{{ item.nightWeather }}<span v-if="item.nightTemperature !== null">（{{ item.nightTemperature }}°C）</span></p>
            <p v-if="item.windDirection"><strong>风向：</strong>{{ item.windDirection }}</p>
            <p v-if="item.windPower"><strong>风力：</strong>{{ item.windPower }}</p>
          </div>
        </div>
      </el-card>

      <el-row :gutter="16" class="main-row">
        <el-col :xs="24" :lg="10">
          <el-card class="panel full-height" shadow="hover">
            <template #header>
              <div class="panel-title">
                <el-icon><Location /></el-icon>
                <span>每日行程</span>
              </div>
            </template>

            <el-tabs v-model="activeDayIndex" class="day-tabs" stretch>
              <el-tab-pane
                v-for="(day, index) in tripPlan.days"
                :key="`${day.title}-${index}`"
                :label="`Day ${index + 1}`"
                :name="index"
              >
                <h3 class="day-title">{{ day.title }}</h3>
                <p v-if="day.date" class="day-sub">{{ day.date }}</p>
                <p v-if="day.description" class="day-tip">{{ day.description }}</p>

                <div class="day-details">
                  <div v-if="day.accommodation || day.hotel" class="detail-block">
                    <h4>住宿</h4>
                    <p v-if="day.accommodation">{{ day.accommodation }}</p>
                    <template v-if="day.hotel">
                      <p v-if="day.hotel.name"><strong>酒店：</strong>{{ day.hotel.name }}</p>
                      <p v-if="day.hotel.priceRange"><strong>类型：</strong>{{ day.hotel.priceRange }}</p>
                      <p v-if="day.hotel.cost !== null"><strong>费用：</strong>{{ day.hotel.cost }}</p>
                      <p v-if="day.hotel.distance"><strong>位置：</strong>{{ day.hotel.distance }}</p>
                      <p v-if="day.hotel.address"><strong>地址：</strong>{{ day.hotel.address }}</p>
                      <p v-if="day.hotel.rating !== null"><strong>评分：</strong>{{ day.hotel.rating }}</p>
                    </template>
                  </div>

                  <div v-if="day.meals.length" class="detail-block">
                    <h4>餐饮</h4>
                    <div v-for="(meal, mealIndex) in day.meals" :key="`${meal.name}-${mealIndex}`" class="meal-item">
                      <strong>{{ mealTypeLabelMap[meal.type] || meal.type || '餐饮' }}：</strong>
                      <span>{{ meal.name }}</span>
                      <span v-if="meal.cost !== null">（{{ meal.cost }}）</span>
                      <p v-if="meal.description">{{ meal.description }}</p>
                      <small v-if="meal.address">{{ meal.address }}</small>
                    </div>
                  </div>

                  <div v-if="day.transportation !== null && day.transportation !== undefined" class="detail-block">
                    <h4>交通</h4>
                    <p>交通预算：{{ day.transportation }}</p>
                  </div>
                </div>

                <el-empty v-if="!day.attractions.length" description="这一天暂无景点" :image-size="80" />

                <div v-else class="attraction-list">
                  <div
                    v-for="(item, idx) in day.attractions"
                    :key="`${item.name}-${idx}`"
                    class="attraction-item"
                    @click="focusAttraction(item)"
                  >
                    <span class="index">{{ idx + 1 }}</span>
                    <div class="attraction-photo">
                      <img
                        v-if="getAttractionPhotoUrl(item)"
                        :src="getAttractionPhotoUrl(item)"
                        :alt="item.name"
                        loading="lazy"
                      />
                      <div v-else-if="isAttractionPhotoLoading(item)" class="photo-placeholder">加载中...</div>
                      <div v-else class="photo-placeholder">暂无图片</div>
                    </div>
                    <div class="content">
                      <h4>{{ item.name }}</h4>
                      <p>{{ item.description }}</p>
                      <p class="attraction-meta">
                        <span v-if="item.category">{{ item.category }}</span>
                        <span v-if="item.rating !== null">评分 {{ item.rating }}</span>
                        <span v-if="item.ticketPrice !== null">门票 {{ item.ticketPrice }}</span>
                        <span v-if="item.visitDuration !== null">{{ item.visitDuration }} 分钟</span>
                      </p>
                      <small v-if="item.address">{{ item.address }}</small>
                      <el-button
                        v-if="isAttractionPhotoError(item)"
                        type="primary"
                        link
                        size="small"
                        @click.stop="retryFetchAttractionPhoto(item)"
                      >
                        重试获取图片
                      </el-button>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="14">
          <el-card class="panel full-height" shadow="hover">
            <template #header>
              <div class="panel-title">
                <el-icon><Location /></el-icon>
                <span>地图预览 (当前 Day)</span>
              </div>
            </template>
            <MapContainer v-if="selectedDayHasCoordinates" height="520px" @ready="onMapReady" />
            <el-empty v-else description="当前天没有可展示的地图坐标" :image-size="80" />
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-empty
      v-else
      :description="parseError || '暂无行程结果，请返回首页生成后查看'"
      class="empty-wrapper"
    >
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </el-empty>
  </div>
</template>

<style scoped>
.result-page {
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(160deg, #f8faff 0%, #eef3ff 100%);
}

.result-card {
  max-width: 1280px;
  margin: 0 auto;
  border-radius: 18px;
  border: none;
}

.header-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.header-row h2 {
  margin: 0;
  font-size: 26px;
}

.header-row p {
  margin: 8px 0 0;
  color: #606266;
  display: flex;
  gap: 6px;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.panel {
  border-radius: 14px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.meta-row,
.main-row {
  margin-bottom: 16px;
}

.overall-text {
  margin: 0;
  line-height: 1.7;
  color: #303133;
  white-space: pre-wrap;
}

.budget-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.budget-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #f5f7fa;
}

.weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.weather-item {
  padding: 12px;
  background: #f6f9ff;
  border: 1px solid #e2ebff;
  border-radius: 10px;
}

.weather-item h4,
.weather-item p {
  margin: 0 0 6px;
}

.overview-list,
.day-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.overview-item,
.detail-block {
  padding: 10px 12px;
  border-radius: 10px;
  background: #f7f9ff;
  border: 1px solid #e5ecff;
}

.overview-item span,
.detail-block h4 {
  display: block;
  margin: 0 0 6px;
  color: #606266;
  font-size: 13px;
}

.overview-item strong {
  color: #303133;
}

.meal-item {
  padding: 8px 0;
  border-top: 1px dashed #dcdfe6;
}

.meal-item:first-of-type {
  border-top: none;
  padding-top: 0;
}

.meal-item p,
.meal-item small {
  margin: 4px 0 0;
  color: #606266;
}

.attraction-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #909399;
  font-size: 12px;
}

.attraction-meta span {
  padding: 2px 8px;
  border-radius: 999px;
  background: #f2f6fc;
}

.full-height {
  height: 100%;
}

.day-tabs {
  min-height: 480px;
}

.day-title {
  margin: 0;
}

.day-sub,
.day-tip {
  margin: 8px 0;
  color: #606266;
}

.attraction-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attraction-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #ebeef5;
  cursor: pointer;
  transition: all 0.2s ease;
}

.attraction-photo {
  width: 86px;
  min-width: 86px;
  height: 86px;
  border-radius: 10px;
  overflow: hidden;
  background: #f4f6fa;
  border: 1px solid #ebeef5;
}

.attraction-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 12px;
}

.attraction-item:hover {
  border-color: #409eff;
  background: #f2f8ff;
}

.index {
  min-width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.content h4 {
  margin: 0;
}

.content p {
  margin: 6px 0;
  color: #606266;
}

.content small {
  color: #909399;
}

.empty-wrapper {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .result-page {
    padding: 12px;
  }

  .header-row {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    width: 100%;
  }
}
</style>
