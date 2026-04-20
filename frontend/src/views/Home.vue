<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generateTripPlan } from '@/services/api.js'
import { Location, MapLocation } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const formRef = ref()

const preferenceOptions = ['文化', '美食', '自然', '购物', '亲子', '夜生活']

const formData = reactive({
  city: '',
  start_date: '',
  end_date: '',
  transportation: '',
  accommodation: '',
  preferences: [],
  additional_request: ''
})

const validateEndDate = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请选择结束日期'))
    return
  }
  if (formData.start_date && value < formData.start_date) {
    callback(new Error('结束日期不能早于开始日期'))
    return
  }
  callback()
}

const rules = {
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    { validator: validateEndDate, trigger: 'change' }
  ],
  transportation: [{ required: true, message: '请选择交通方式', trigger: 'change' }],
  preferences: [{ type: 'array', required: false, trigger: 'change' }]
}

const resetForm = () => {
  formRef.value?.resetFields()
}

const onSubmit = async () => {
  if (loading.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请先修正表单校验错误')
    return
  }

  const payload = {
    city: formData.city.trim(),
    start_date: formData.start_date,
    end_date: formData.end_date,
    transportation: formData.transportation,
    accommodation: formData.accommodation ? formData.accommodation : null,
    preferences: formData.preferences,
    additional_request: formData.additional_request.trim() || null
  }

  loading.value = true
  try {
    const data = await generateTripPlan(payload)
    // sessionStorage.setItem('tripPlan', JSON.stringify(data))

    localStorage.setItem('tripPlan', JSON.stringify(data))

    ElMessage.success('行程规划生成成功')
    await router.push('/result')
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || '生成失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="home-page">
    <div class="bg-decoration"></div>

    <el-card class="trip-card" shadow="always">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><MapLocation /></el-icon>
          <div class="header-text">
            <h2>AI 智能旅行规划</h2>
            <p>告诉 Agent 你的想法，开启专属行程</p>
          </div>
        </div>
      </template>

      <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-position="top"
          status-icon
          class="custom-form"
      >
        <el-form-item label="你想去哪儿？" prop="city">
          <el-input
              v-model="formData.city"
              placeholder="输入目的地，如：成都、巴黎..."
              :prefix-icon="Location"
              clearable
          />
        </el-form-item>

        <div class="form-row">
          <el-form-item label="开始日期" prop="start_date" class="flex-1">
            <el-date-picker
                v-model="formData.start_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="出发日期"
            />
          </el-form-item>
          <div class="date-separator">至</div>
          <el-form-item label="结束日期" prop="end_date" class="flex-1">
            <el-date-picker
                v-model="formData.end_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="返程日期"
            />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="交通偏好" prop="transportation" class="flex-1">
            <el-select v-model="formData.transportation" placeholder="选择出行方式">
              <el-option label="公共交通" value="公共交通" />
              <el-option label="自驾" value="自驾" />
              <el-option label="打车" value="打车" />
              <el-option label="步行" value="步行" />
            </el-select>
          </el-form-item>
          <el-form-item label="住宿标准" class="flex-1">
            <el-select v-model="formData.accommodation" placeholder="可选（默认舒适）" clearable>
              <el-option label="经济型" value="经济型酒店" />
              <el-option label="舒适型" value="舒适型酒店" />
              <el-option label="高端奢华" value="高端酒店" />
              <el-option label="特色民宿" value="民宿" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="旅行偏好 (多选)" prop="preferences">
          <el-checkbox-group v-model="formData.preferences" class="preference-group">
            <el-checkbox-button v-for="item in preferenceOptions" :key="item" :value="item">
              {{ item }}
            </el-checkbox-button>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="更多个性化需求">
          <el-input
              v-model="formData.additional_request"
              type="textarea"
              :rows="3"
              placeholder="例如：我喜欢摄影，请多安排出片的地方；或是避开爬山项目..."
              maxlength="200"
              show-word-limit
          />
        </el-form-item>

        <div class="form-actions">
          <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="onSubmit"
          >
            {{ loading ? 'AI 正在全力规划中...' : '开始生成行程' }}
          </el-button>
          <el-button size="large" @click="resetForm" plain>清空重置</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
/* 容器背景优化 */
.home-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  /* 使用更具旅行感的渐变背景 */
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  position: relative;
  overflow: hidden;
}

/* 增强科技感的装饰球 */
.bg-decoration {
  position: absolute;
  top: -150px;
  right: -150px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.15) 0%, rgba(64, 158, 255, 0) 70%);
  border-radius: 50%;
  z-index: 0;
}

.trip-card {
  width: 100%;
  max-width: 600px; /* 稍微缩小宽度更显精致 */
  border-radius: 20px;
  border: none;
  z-index: 1;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 10px 5px;
}

/* 修复 SVG 图标过大的关键样式 */
.header-icon {
  /* 控制图标容器，避免标题区被放大 */
  width: 40px;
  height: 40px;

  /* 2. 内部 SVG 居中 */
  display: flex;
  align-items: center;
  justify-content: center;

  /* 图标本体大小 */
  font-size: 20px;

  /* 4. 其他修饰样式 */
  color: #409eff;
  background: rgba(64, 158, 255, 0.1); /* 浅蓝色背景 */
  border-radius: 10px;
  margin-right: 12px;
  flex-shrink: 0; /* 防止图标在小屏下被压缩 */
}

/* 避免被全局 svg 规则意外放大 */
.header-icon :deep(svg) {
  width: 1em;
  height: 1em;
}

.header-text h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-text p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #909399;
}

/* 表单布局优化 */
.custom-form {
  margin-top: 10px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.flex-1 {
  flex: 1;
}

/* 强制日期选择器占满宽度 */
:deep(.el-date-editor.el-input),
:deep(.el-date-editor.el-input__wrapper),
:deep(.el-select) {
  width: 100% !important;
}

/* 偏好选择组样式优化 */
.preference-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.el-checkbox-button__inner) {
  border-radius: 8px !important;
  border: 1px solid #dcdfe6 !important;
  margin-right: 0; /* 靠 gap 控制 */
  padding: 8px 16px;
  background: #fdfdfd;
  transition: all 0.3s;
}

:deep(.el-checkbox-button.is-checked .el-checkbox-button__inner) {
  background-color: #409eff !important;
  border-color: #409eff !important;
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.3) !important;
}

/* 操作按钮 */
.form-actions {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.submit-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 12px;
  background: linear-gradient(90deg, #409eff, #53a8ff);
  border: none;
}

.submit-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 响应式微调 */
@media (max-width: 540px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  .trip-card {
    border-radius: 0; /* 手机端全屏感 */
    box-shadow: none;
  }
  .home-page {
    padding: 0;
    align-items: flex-start;
    background: #fff;
  }

  .header-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
}
</style>