<template>
  <div class="config-editor">
    <el-card class="box-card" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>公共字段配置 (Global Fields)</span>
          <el-button type="primary" size="small" @click="addGlobalField">新增字段</el-button>
        </div>
      </template>
      <el-table :data="config.global_fields" style="width: 100%" border>
        <el-table-column prop="label" label="显示名称" width="180">
          <template #default="{ row }">
            <el-input v-model="row.label" placeholder="Project Name" />
          </template>
        </el-table-column>
        <el-table-column prop="key" label="字段Key" width="180">
          <template #default="{ row }">
            <el-input v-model="row.key" placeholder="project_name" />
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型">
          <template #default="{ row }">
            <el-select v-model="row.type" placeholder="Select">
              <el-option label="Text" value="text" />
              <el-option label="Date" value="date" />
              <el-option label="Textarea" value="textarea" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ $index }">
            <el-button type="danger" circle :icon="Delete" @click="removeGlobalField($index)" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>步骤类型配置 (Step Types)</span>
          <el-button type="success" size="small" @click="addStepType">新增步骤类型</el-button>
        </div>
      </template>
      
      <el-collapse accordion>
        <el-collapse-item v-for="(step, key) in config.step_types" :key="key" :name="key">
          <template #title>
            <div style="display: flex; justify-content: space-between; width: 100%; align-items: center; padding-right: 10px;">
               <span style="font-weight: bold; margin-right: 10px;">{{ step.name || key }}</span>
               <el-tag size="small">{{ key }}</el-tag>
            </div>
          </template>
          
          <el-form label-width="120px">
            <el-form-item label="类型标识(Key)">
              <!-- Key is the object key, tricky to edit directly in loop -->
              <el-input v-model="step._key" disabled placeholder="unique_key" />
              <div class="tip">Key 只能在创建时指定 (Key cannot be changed once created)</div>
            </el-form-item>
            <el-form-item label="显示名称">
              <el-input v-model="step.name" />
            </el-form-item>
            <el-form-item label="模板文件">
              <el-input v-model="step.template_file" placeholder="step_xxx.docx" />
              <div class="tip">请确保 templates/steps/ 下存在该文件</div>
            </el-form-item>
            
            <div class="sub-header">
              <span>字段定义 (Fields)</span>
              <el-button type="primary" link @click="addStepField(step)">+ 添加字段</el-button>
            </div>
            
            <el-table :data="step.fields" style="width: 100%" size="small" border>
              <el-table-column prop="label" label="Label">
                <template #default="{ row }">
                  <el-input v-model="row.label" />
                </template>
              </el-table-column>
              <el-table-column prop="key" label="Key">
                <template #default="{ row }">
                  <el-input v-model="row.key" />
                </template>
              </el-table-column>
               <el-table-column prop="type" label="Type" width="120">
                <template #default="{ row }">
                  <el-select v-model="row.type" size="small">
                    <el-option label="Text" value="text" />
                    <el-option label="Date" value="date" />
                    <el-option label="Textarea" value="textarea" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="Op" width="60">
                <template #default="{ $index }">
                  <el-button type="danger" link :icon="Delete" @click="removeStepField(step, $index)" />
                </template>
              </el-table-column>
            </el-table>

            <div style="margin-top: 15px; text-align: right;">
              <el-popconfirm title="确定删除这个步骤类型吗?" @confirm="removeStepType(key)">
                <template #reference>
                  <el-button type="danger" size="small">删除步骤类型</el-button>
                </template>
              </el-popconfirm>
            </div>

          </el-form>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <div class="actions">
      <el-button type="primary" size="large" @click="saveConfig" :loading="saving">保存配置 (Save Configuration)</el-button>
    </div>

    <!-- Dialog for New Step Type -->
    <el-dialog v-model="showAddStepDialog" title="新建步骤类型">
      <el-form :model="newStepForm">
        <el-form-item label="Key (Unique)" required>
          <el-input v-model="newStepForm.key" placeholder="e.g. redis_update" />
        </el-form-item>
        <el-form-item label="Name" required>
          <el-input v-model="newStepForm.name" placeholder="Redis Update" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddStepDialog = false">Cancel</el-button>
          <el-button type="primary" @click="confirmAddStepType">Confirm</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const config = ref({ global_fields: [], step_types: {} })
const saving = ref(false)
const showAddStepDialog = ref(false)
const newStepForm = ref({ key: '', name: '' })

// API Base URL
const API_BASE = ''

const loadConfig = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/config/`)
    // Add _key to step types for display/logic
    const data = res.data
    for(let key in data.step_types) {
      data.step_types[key]._key = key
    }
    config.value = data
  } catch (e) {
    ElMessage.error('Failed to load config: ' + e.message)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    // Clean up _key before saving
    const dataToSave = JSON.parse(JSON.stringify(config.value))
    for(let key in dataToSave.step_types) {
      delete dataToSave.step_types[key]._key
    }
    
    await axios.put(`${API_BASE}/api/config/`, dataToSave)
    ElMessage.success('Configuration saved successfully!')
  } catch (e) {
    ElMessage.error('Failed to save: ' + e.message)
  } finally {
    saving.value = false
  }
}

// Global Field Operations
const addGlobalField = () => {
  config.value.global_fields.push({ key: '', label: '', type: 'text' })
}
const removeGlobalField = (index) => {
  config.value.global_fields.splice(index, 1)
}

// Step Type Operations
const addStepType = () => {
  newStepForm.value = { key: '', name: '' }
  showAddStepDialog.value = true
}

const confirmAddStepType = () => {
  const k = newStepForm.value.key
  if(!k) return ElMessage.warning('Key is required')
  if(config.value.step_types[k]) return ElMessage.warning('Key already exists')
  
  config.value.step_types[k] = {
    _key: k,
    name: newStepForm.value.name,
    template_file: '',
    fields: []
  }
  showAddStepDialog.value = false
}

const removeStepType = (key) => {
  delete config.value.step_types[key]
}

const addStepField = (step) => {
  if(!step.fields) step.fields = []
  step.fields.push({ key: '', label: '', type: 'text' })
}

const removeStepField = (step, index) => {
  step.fields.splice(index, 1)
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.config-editor {
  max-width: 900px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sub-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 5px;
  font-size: 14px;
  color: #606266;
  border-top: 1px dashed #eee;
  padding-top: 10px;
}
.actions {
  margin-top: 20px;
  text-align: center;
  position: sticky;
  bottom: 20px;
  background: rgba(255,255,255,0.8);
  padding: 10px;
  backdrop-filter: blur(5px);
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}
.tip {
  font-size: 12px;
  color: #909399;
}
</style>
