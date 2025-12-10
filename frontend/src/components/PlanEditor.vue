<template>
  <div class="plan-editor">
    
    <!-- Top Actions -->
    <div class="top-bar">
      <el-button @click="backToList" :icon="Back">Back to List</el-button>
      <div class="right-actions">
        <el-button type="success" @click="savePlan" :loading="saving">Save Plan</el-button>
        <el-button type="primary" @click="generateDoc" :loading="generating">Generate Document</el-button>
      </div>
    </div>

    <!-- Main Content -->
    <el-row :gutter="20">
      <!-- Left: Global Info -->
      <el-col :span="8">
        <el-card header="基本信息 (Basic Info)">
          <el-form label-position="top">
            <el-form-item label="Plan Filename">
              <el-input v-model="plan.filename" placeholder="plan_v1.0.json" />
            </el-form-item>
            
            <!-- Dynamic Global Fields -->
            <el-form-item v-for="(field, idx) in config.global_fields" :key="idx" :label="field.label">
              <el-date-picker v-if="field.type === 'date'" v-model="plan[field.key]" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              <el-input v-else-if="field.type === 'textarea'" type="textarea" v-model="plan[field.key]" />
              <el-input v-else v-model="plan[field.key]" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- Right: Steps -->
      <el-col :span="16">
        <el-card header="上线步骤 (Deployment Steps)">
          
          <div v-if="plan.steps.length === 0" class="empty-steps">
            No steps added. Click buttons below to add steps.
          </div>
          
          <el-collapse>
            <el-collapse-item v-for="(step, idx) in plan.steps" :key="idx">
               <template #title>
                 <div class="step-title">
                   <span class="step-seq">{{ idx + 1 }}.</span>
                    <span class="step-name">{{ getStepName(step) }}</span>
                    <div class="step-ops" @click.stop>
                      <el-button size="small" circle :icon="Top" @click="moveStep(idx, -1)" :disabled="idx === 0" />
                      <el-button size="small" circle :icon="Bottom" @click="moveStep(idx, 1)" :disabled="idx === plan.steps.length - 1" />
                      <el-button size="small" type="danger" circle :icon="Delete" @click="removeStep(idx)" />
                    </div>
                 </div>
               </template>
               
               <!-- Dynamic Step Form -->
               <el-form label-width="120px" size="small">
                 
                 <!-- ROLLBACK MODE: Description Only -->
                 <div v-if="step.data.is_rollback">
                    <el-form-item label="回退说明 (Rollback Desc)">
                      <el-input type="textarea" :rows="3" v-model="step.data.rollback_desc" placeholder="Enter rollback instructions here..." />
                    </el-form-item>
                 </div>

                 <!-- NORMAL MODE: Render Common Fields -->
                 <div v-else-if="getStepFields(step.type).length > 0">
                   <div v-for="(field, fIdx) in getStepFields(step.type)" :key="fIdx">
                     <el-form-item :label="field.label">
                        <el-date-picker v-if="field.type === 'date'" v-model="step.data[field.key]" type="date" value-format="YYYY-MM-DD" />
                        <el-input v-else-if="field.type === 'textarea'" type="textarea" :rows="3" v-model="step.data[field.key]" />
                        <el-input v-else v-model="step.data[field.key]" />
                     </el-form-item>
                   </div>
                 </div>

                 <!-- TABLE DATA (if enabled) -->
                 <div v-if="hasTable(step.type)" style="margin-top: 20px;">
                   <div class="sub-label" style="font-weight: bold; margin-bottom: 10px;">列表数据 (Table Data)</div>
                   
                   <el-table :data="getStepItems(step)" style="width: 100%" border size="small">
                     <el-table-column v-for="(field, fIdx) in getStepTableFields(step.type)" :key="fIdx" :label="field.label" :prop="field.key">
                       <template #default="scope">
                          <el-date-picker v-if="field.type === 'date'" v-model="scope.row[field.key]" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
                          <el-input v-else-if="field.type === 'textarea'" type="textarea" :rows="1" v-model="scope.row[field.key]" />
                          <el-input v-else v-model="scope.row[field.key]" />
                       </template>
                     </el-table-column>
                     <el-table-column label="Op" width="60">
                       <template #default="scope">
                         <el-button type="danger" link :icon="Delete" @click="removeStepItem(step, scope.$index)" />
                       </template>
                     </el-table-column>
                   </el-table>
                   <el-button size="small" type="primary" link style="margin-top: 5px" @click="addStepItem(step)">+ Add Row</el-button>
                 </div>

               </el-form>
            </el-collapse-item>
          </el-collapse>
          
          <el-divider>Add Step</el-divider>
          
          <div class="add-step-zone">
            <el-button v-for="(sConfig, key) in config.step_types" :key="key" @click="addStep(key)">
              + {{ sConfig.name }}
            </el-button>
          </div>

        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import axios from 'axios'
import { Back, Top, Bottom, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props: planFilename (if editing existing), defaults to null
const props = defineProps(['filename', 'sourceFilename'])
const emit = defineEmits(['back'])

const config = ref({ global_fields: [], step_types: {} })
const plan = ref({ filename: '', steps: [] })
const saving = ref(false)
const generating = ref(false)

const API_BASE = ''

const loadConfig = async () => {
  const res = await axios.get(`${API_BASE}/api/config/`)
  config.value = res.data
}

const loadPlan = async () => {
  if (props.filename) {
    try {
      const res = await axios.get(`${API_BASE}/api/plans/${props.filename}`)
      plan.value = res.data
      // Ensure steps is array
      if(!plan.value.steps) plan.value.steps = []
    } catch(e) {
      ElMessage.error('Failed to load plan')
    }
  } else if (props.sourceFilename) {
    // CLONE MODE
    try {
      const res = await axios.get(`${API_BASE}/api/plans/${props.sourceFilename}`)
      plan.value = res.data
      
      // Reset identity for the new copy
      // Modify filename to indicate copy
      if (plan.value.filename && plan.value.filename.endsWith('.json')) {
         plan.value.filename = plan.value.filename.replace('.json', '_copy.json')
      } else {
         plan.value.filename = (plan.value.filename || 'plan') + '_copy'
      }
      
      // Reset date to today? Or keep? Let's reset to today for a new deployment
      // Actually let's just clear it or let the user decide. 
      // Often a clone is for a different date.
      // plan.value.deploy_date = '' // Optional: clear date
      
      // Ensure steps is array
      if(!plan.value.steps) plan.value.steps = []
      
    } catch(e) {
      ElMessage.error('Failed to load source plan for cloning')
    }
  } else {
    // New Plan defaults
    plan.value.steps = []
  }
}

// Helpers
const getStepName = (step) => {
  let name = config.value.step_types[step.type]?.name || step.type
  if (step.data && step.data.is_rollback) {
    name += " (Rollback)"
  }
  return name
}
const getStepFields = (type) => {
  return config.value.step_types[type]?.fields || []
}
const getStepTableFields = (type) => {
  return config.value.step_types[type]?.table_fields || []
}
const hasTable = (type) => {
  return config.value.step_types[type]?.has_table || config.value.step_types[type]?.is_table || false
}

// Actions
const addStep = (type) => {
  // Add Deployment Step
  plan.value.steps.push({
    type: type,
    data: {} 
  });
  // Add Rollback Step
  plan.value.steps.push({
    type: type,
    data: { is_rollback: true, rollback_desc: '' } 
  });
}

const removeStep = (idx) => {
  plan.value.steps.splice(idx, 1)
}

const moveStep = (idx, dir) => {
  const item = plan.value.steps[idx]
  plan.value.steps.splice(idx, 1)
  plan.value.steps.splice(idx + dir, 0, item)
}



const getStepItems = (step) => {
  // Ensure data.items exists
  if (!step.data.items || !Array.isArray(step.data.items)) {
    step.data.items = []
  }
  return step.data.items
}

const addStepItem = (step) => {
  if (!step.data.items) step.data.items = []
  step.data.items.push({})
}

const removeStepItem = (step, index) => {
  if (step.data.items) step.data.items.splice(index, 1)
}

const savePlan = async () => {
  saving.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/plans/`, plan.value)
    plan.value.filename = res.data.filename
    ElMessage.success('Saved!')
  } catch(e) {
    ElMessage.error('Save failed: ' + e.message)
  } finally {
    saving.value = false
  }
}

const generateDoc = async () => {
  generating.value = true
  try {
    // We send the FULL plan data to generate, not just ID, to ensure WYSIWYG
    // Or we save first? Best to save first.
    await savePlan()
    
    const res = await axios.post(`${API_BASE}/api/plans/generate`, plan.value, {
      responseType: 'blob'
    })
    
    // Download logic
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    
    // Try to get filename from headers
    const contentDisp = res.headers['content-disposition']
    let fileName = 'Plan.docx';
    if(contentDisp) {
        const match = contentDisp.match(/filename=(.+)/);
        if(match) fileName = match[1];
    }
    
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    ElMessage.success('Document Generated!')
    
  } catch(e) {
    ElMessage.error('Generation failed: ' + e.message)
  } finally {
    generating.value = false
  }
}

const backToList = () => {
  emit('back')
}

onMounted(async () => {
  await loadConfig()
  await loadPlan()
})

</script>

<style scoped>
.plan-editor {
  padding-bottom: 50px;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}
.step-title {
  display: flex;
  align-items: center;
  width: 100%;
}
.step-seq {
  font-weight: bold;
  margin-right: 10px;
  width: 20px;
}
.step-name {
  flex: 1;
  font-weight: 500;
}
.step-ops {
  margin-right: 10px;
}
.add-step-zone {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-start;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}
.empty-steps {
  padding: 40px;
  text-align: center;
  color: #909399;
  border: 2px dashed #e4e7ed;
  margin-bottom: 20px;
}
</style>
