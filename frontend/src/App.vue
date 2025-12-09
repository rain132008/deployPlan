<template>
  <el-container>
    <el-header>
      <div class="logo">AutoDeployDocs 🚀</div>
      <div class="nav">
        <el-button link @click="view = 'list'">Plans</el-button>
        <el-button link @click="view = 'config'">Configuration</el-button>
      </div>
    </el-header>
    
    <el-main>
      
      <!-- PLAN LIST VIEW -->
      <div v-if="view === 'list'" class="plan-list-view">
        <div class="list-header">
           <h2>Deployment Plans</h2>
           <el-button type="primary" @click="createNewPlan">+ New Plan</el-button>
        </div>
        
        <el-table :data="plans" style="width: 100%" v-loading="loading">
          <el-table-column prop="filename" label="Filename" width="220" />
          <el-table-column prop="version" label="Version" width="120" />
          <el-table-column prop="deploy_date" label="Date" width="120" />
          <el-table-column prop="owner" label="Owner" />
          <el-table-column label="Actions" width="150" align="right">
            <template #default="scope">
              <el-button v-if="scope && scope.row" size="small" @click="editPlan(scope.row.filename)">Edit</el-button>
              <el-button v-if="scope && scope.row" size="small" type="success" @click="clonePlan(scope.row.filename)">Clone</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- CONFIG VIEW -->
      <ConfigEditor v-if="view === 'config'" />

      <!-- PLAN EDITOR VIEW -->
      <PlanEditor v-if="view === 'editor'" :filename="currentPlanFile" :source-filename="sourcePlanFile" @back="view = 'list'; loadPlans()" />

    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ConfigEditor from './components/ConfigEditor.vue'
import PlanEditor from './components/PlanEditor.vue'
import { ElMessage } from 'element-plus'

const view = ref('list') // list, config, editor
const plans = ref([])
const loading = ref(false)
const currentPlanFile = ref(null)
const sourcePlanFile = ref(null)

const API_BASE = ''

const loadPlans = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/plans/`)
    plans.value = res.data
  } catch(e) {
    ElMessage.error('Failed to load plans')
  } finally {
    loading.value = false
  }
}

const createNewPlan = () => {
  currentPlanFile.value = null
  sourcePlanFile.value = null
  view.value = 'editor'
}

const editPlan = (filename) => {
  currentPlanFile.value = filename
  sourcePlanFile.value = null
  view.value = 'editor'
}

const clonePlan = (filename) => {
  currentPlanFile.value = null
  sourcePlanFile.value = filename
  view.value = 'editor'
}

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.plan-list-view {
  max-width: 1000px;
  margin: 0 auto;
}
</style>
