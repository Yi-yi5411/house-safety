<template>
  <view class="container">
    <view class="top-bar">
      <button class="btn-txt" @click="goBack">← 返回构件列表</button>
      <view class="nav-btns">
        <button v-if="typePos>0" class="btn-txt" @click="goPrev">← 上一个</button>
        <button v-if="typePos<allTypes.length-1" class="btn-txt" @click="goNext">下一个 →</button>
      </view>
    </view>

    <view class="title-row"><text class="title">{{ compType }}</text><text class="cat">{{ compCat }}</text></view>

    <view v-if="loading" class="loading">加载中...</view>

    <view v-else>
      <!-- 轴线实例 -->
      <view class="sec">
        <text class="slabel">构件轴线 / 位置</text>
        <view class="ar" v-if="checks.length>0"><text class="edit-hint">当前构件：</text><input :value="checks[idx]?.axisLine||''" placeholder="轴号/位置" class="ai" @input="e=>{checks[idx].axisLine=e.detail.value}"/></view>
        <view class="ar"><input v-model="newAxis" placeholder="例如：1-2轴交A轴、东" class="ai" @confirm="doAdd"/><button class="btn green" @click="doAdd">新增构件</button></view>
        <view class="tabs" v-if="checks.length>0">
          <view v-for="(c,i) in checks" :key="c._k" class="tab" :class="{on:i===idx}">
            <text @click="switchTab(i)">构件{{i+1}}</text>
            <text class="tax" @tap.stop="editAxis(i)">({{c.axisLine||'无轴号'}})</text>
            <button class="tx" @click.stop="delCheck(i)">×</button>
          </view>
        </view>
      </view>

      <!-- 评定标准 -->
      <view class="sec">
        <text class="slabel">评定标准 ({{matchedStd.length}}条)</text>
        <text v-if="matchedStd.length===0" class="hint">暂未匹配到评定标准 (共加载{{stdAll.length}}条)</text>
        <view v-for="g in groupedStd" :key="g.result" class="sg">
          <view class="sgh"><view class="sd" :style="{background:g.color}"></view><text class="sgt">{{g.result}}</text><text class="sgn">{{g.items.length}}项</text></view>
          <view v-for="s in g.items" :key="s.id" class="sr" @click="toggleStd(s.id)">
            <button class="scb" @click.stop="toggleStd(s.id)">{{cIds.includes(s.id)?'☑':'☐'}}</button>
            <view class="sb">
              <view class="sdsc"><text v-for="(seg,si) in parseDesc(s.description)" :key="si"><text v-if="seg.t==='t'">{{seg.v}}</text><input v-else class="dci" type="number" :value="gdv(s.id,seg.idx)" :disabled="!cIds.includes(s.id)" @click.stop @input.stop="e=>sdv(s.id,seg.idx,e.detail.value)"/></text></view>
              <view class="sm"><text class="sbg" :style="{background:getColor(s.evaluationResult||s.evaluation_result)}">{{s.evaluationResult||s.evaluation_result}}</text><text class="scl" v-if="s.evaluationClause||s.evaluation_clause">{{s.evaluationClause||s.evaluation_clause}}</text></view>
            </view>
          </view>
        </view>
      </view>

      <!-- 确认评定 -->
      <view class="sec" v-if="cIds.length>0">
        <button class="btn-a" @click="doAssess">确认评定</button>
        <view v-if="result" class="ac"><text class="aclbl">评定结果：</text><text class="av" :style="{color:getColor(result)}">{{result}}</text><text v-if="clause" class="aclref">（依据：{{clause}}）</text></view>
      </view>

      <!-- 照片 -->
      <view class="sec"><text class="slabel">检测照片</text><ImageUploader v-model="photos" :max-count="9"/></view>

      <!-- 保存 -->
      <button class="btn-s" @click="doSave">保存当前构件</button>
      <view class="btm-nav">
        <button v-if="typePos>0" class="btn-txt" @click="goPrev">← 返回上一个构件</button>
        <button v-if="typePos<allTypes.length-1" class="btn-txt" @click="goNext">进入下一个构件 →</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getComponentCheckList, createComponentCheck, updateComponentCheck, deleteComponentCheck, getEvaluationStandards } from '@/api/damage-component.js'
import ImageUploader from '@/components/ImageUploader.vue'

const sv = ref(''); const compType = ref(''); const compCat = ref('')
const checks = ref([]); const idx = ref(0); const newAxis = ref('')
const stdAll = ref([]); const loading = ref(true)
const cIds = ref([]); const dValues = ref({}); const result = ref(''); const clause = ref(''); const checkId = ref('')
const allTypes = ref([]); const typePos = ref(-1)
const photos = ref([])

// ---- READ-ONLY computed (never mutates!) ----
const matchedStd = computed(() => {
  const f = stdAll.value.filter(s => (s.componentType||s.component_type) === compType.value)
  return f.length > 0 ? f : stdAll.value.filter(s => (s.category||'') === compCat.value)
})
const groupedStd = computed(() => {
  const p = {处于危险状态:5,危险状态:5,危险点:5,严重损坏:4,一般损坏:3,'地基稳定，但上部结构倾斜存在安全隐患':3,基本完好:2,非危险状态:1,完好:1}
  const colors = {完好:'#2EA65E',非危险状态:'#2EA65E',基本完好:'#226CB3',一般损坏:'#E28A13',严重损坏:'#D43535','地基稳定，但上部结构倾斜存在安全隐患':'#E28A13',处于危险状态:'#D43535',危险状态:'#D43535',危险点:'#D43535',危险:'#D43535'}
  const g = {}
  matchedStd.value.forEach(s => {
    const k = s.evaluationResult||s.evaluation_result||'其他'
    if(!g[k])g[k]=[]
    g[k].push(s)
  })
  return Object.entries(g).sort(([a],[b])=>(p[a]||0)-(p[b]||0)).map(([r,items])=>({result:r,items,color:colors[r]||'#626F7D'}))
})

// ---- Helpers ----
function getCat(t){return['混凝土柱','砖柱','砖墙','混凝土梁','混凝土板','屋架'].includes(t)?'上部承重结构':['砌体自承重墙','承担水平荷载的填充墙','门窗洞口过梁','挑梁','雨棚板','女儿墙'].includes(t)?'围护结构':['地基','基础'].includes(t)?'地基基础':'其他'}
function getColor(r){return({'完好':'#2EA65E','基本完好':'#226CB3','一般损坏':'#E28A13','严重损坏':'#D43535','危险':'#D43535','危险状态':'#D43535'})[r]||'#626F7D'}
function buildOrderedTypes(checksList,standardsList){const categoryOrder={'地基基础':0,'上部承重结构':1,'围护结构':2,'其他':3};const sorted=[...standardsList].sort((a,b)=>{const ca=a.category||'';const cb=b.category||'';const diff=(categoryOrder[ca]??99)-(categoryOrder[cb]??99);if(diff!==0)return diff;return(a.sortOrder||a.sort_order||0)-(b.sortOrder||b.sort_order||0)});const typeOrder=[];const seen=new Set();for(const s of sorted){const ct=s.componentType||s.component_type;if(ct&&!seen.has(ct)){seen.add(ct);typeOrder.push(ct)}}const checkTypes=new Set(checksList.map(c=>c.componentType||c.name||c.component_type||'').filter(Boolean));return typeOrder.filter(t=>checkTypes.has(t))}
function syncCheck(i){const c=checks.value[i]||{};checkId.value=c.id||'';cIds.value=[...(c.checkedItemIds||c.checked_item_ids||[])];dValues.value={...(c.descriptionValues||c.description_values||{})};result.value=c.aiEvaluationResult||c.ai_evaluation_result||'';clause.value=c.aiEvaluationClause||c.ai_evaluation_clause||'';photos.value=[...(c.photos||[])]}
function saveCurrentToChecks(){const i=idx.value;if(i<0||i>=checks.value.length)return;const c=checks.value[i];c.checkedItemIds=[...cIds.value];c.descriptionValues={...dValues.value};c.aiEvaluationResult=result.value;c.aiEvaluationClause=clause.value;c.photos=[...photos.value]}
function switchTab(i){if(i===idx.value)return;saveCurrentToChecks();idx.value=i;syncCheck(i)}
function editAxis(i){if(i!==idx.value){saveCurrentToChecks();idx.value=i;syncCheck(i)}}
function toggleStd(id){const a=[...cIds.value];const i=a.indexOf(id);if(i>-1){a.splice(i,1);const d={...dValues.value};delete d[id];dValues.value=d}else a.push(id);cIds.value=a}
function parseDesc(d){if(!d)return[{t:'t',v:''}];const p=[];let l=0,bi=0;const re=/_{2,}/g;let m;while((m=re.exec(d))!==null){if(m.index>l)p.push({t:'t',v:d.slice(l,m.index)});p.push({t:'i',idx:bi,ph:'数值'});l=m.index+m[0].length;bi++}if(l<d.length)p.push({t:'t',v:d.slice(l)});return p.length?p:[{t:'t',v:d}]}
function gdv(sid,i){return(dValues.value[sid]||[])[i]||''}
function sdv(sid,i,v){const d={...dValues.value};if(!d[sid])d[sid]=[];d[sid][i]=v;dValues.value=d}
function doAssess(){if(!cIds.value.length)return uni.showToast({title:'请先勾选标准',icon:'none'});const chk=matchedStd.value.filter(s=>cIds.value.includes(s.id));const p={处于危险状态:5,危险状态:5,危险点:5,严重损坏:4,一般损坏:3,'地基稳定，但上部结构倾斜存在安全隐患':3,基本完好:2,非危险状态:1,完好:1};let w=chk[0];chk.forEach(s=>{if((p[s.evaluationResult||s.evaluation_result]||0)>(p[w.evaluationResult||w.evaluation_result]||0))w=s});result.value=w.evaluationResult||w.evaluation_result;clause.value=w.evaluationClause||w.evaluation_clause||'';uni.showToast({title:'评定完成',icon:'success'})}
function doAdd(){saveCurrentToChecks();const ax=newAxis.value.trim()||'构件'+(checks.value.length+1);checks.value.push({_k:Date.now().toString(36),name:compType.value,category:compCat.value,axisLine:ax,checkedItemIds:[],descriptionValues:{},photos:[],aiEvaluationResult:'',aiEvaluationClause:''});idx.value=checks.value.length-1;syncCheck(idx.value);newAxis.value=''}
function delCheck(i){uni.showModal({title:'确认删除',content:'确定删除该构件吗？',success:async r=>{if(!r.confirm)return;const c=checks.value[i];if(c.id)try{await deleteComponentCheck(c.id)}catch(e){};checks.value.splice(i,1);if(checks.value.length===0){uni.navigateBack();return};if(idx.value>=checks.value.length)idx.value=Math.max(0,checks.value.length-1);syncCheck(idx.value)}})}
async function goBack(){await saveCurrentToServer();uni.navigateBack()}
async function goPrev(){await saveCurrentToServer();await switchToType(typePos.value-1)}
async function goNext(){await saveCurrentToServer();await switchToType(typePos.value+1)}
async function saveCurrentToServer(){saveCurrentToChecks();if(!checkId.value)return;const c=checks.value[idx.value];if(!c)return;try{await updateComponentCheck(checkId.value,{axisLine:c.axisLine||'',checkedItemIds:[...cIds.value],descriptionValues:{...dValues.value},aiEvaluationResult:result.value,aiEvaluationClause:clause.value,photos:[...photos.value]})}catch(e){}}
async function switchToType(pos){
  if(pos<0||pos>=allTypes.value.length)return
  const newType = allTypes.value[pos]
  compType.value = newType
  compCat.value = getCat(newType)
  loading.value = true
  try{
    const r = await getComponentCheckList(sv.value)
    const all = r.items||r||[]
    allTypes.value=buildOrderedTypes(all,stdAll.value)
    typePos.value=allTypes.value.indexOf(newType)
    checks.value = all.filter(c=>(c.componentType||c.name||c.component_type)===newType).map((c,i)=>({...c,_k:c.id||i.toString()}))
    if(checks.value.length===0){checks.value.push({_k:'d',name:newType,category:compCat.value,axisLine:'',checkedItemIds:[],descriptionValues:{},photos:[],aiEvaluationResult:'',aiEvaluationClause:''})}
    idx.value = 0; syncCheck(0); newAxis.value = ''
  }catch(e){console.error(e)}
  loading.value = false
}
async function doSave(){if(!cIds.value.length)return uni.showToast({title:'请勾选评定标准',icon:'none'});saveCurrentToChecks();const p={checkedItemIds:[...cIds.value],descriptionValues:{...dValues.value},aiEvaluationResult:result.value,aiEvaluationClause:clause.value,axisLine:checks.value[idx.value]?.axisLine||'',photos:[...photos.value]};try{let saved;if(checkId.value){saved=await updateComponentCheck(checkId.value,p)}else{saved=await createComponentCheck({name:compType.value,category:compCat.value,survey_id:sv.value,...p});const entry=checks.value[idx.value];if(saved){entry.id=saved.id;entry._k=saved.id;checkId.value=saved.id}};allTypes.value=buildOrderedTypes(checks.value,stdAll.value);typePos.value=allTypes.value.indexOf(compType.value);uni.showToast({title:'保存成功',icon:'success'})}catch(e){uni.showToast({title:'保存失败',icon:'none'})}}

onLoad(async opts=>{sv.value=opts.surveyId||'';compType.value=decodeURIComponent(opts.type||'');compCat.value=getCat(compType.value);try{const[cr,sr]=await Promise.all([getComponentCheckList(sv.value),getEvaluationStandards()]);const all=cr.items||cr||[];stdAll.value=sr.items||sr||[];allTypes.value=buildOrderedTypes(all,stdAll.value);typePos.value=allTypes.value.indexOf(compType.value);checks.value=all.filter(c=>(c.componentType||c.name||c.component_type)===compType.value).map((c,i)=>({...c,_k:c.id||i.toString()}));if(checks.value.length===0){checks.value.push({_k:'d',name:compType.value,category:compCat.value,axisLine:'',checkedItemIds:[],descriptionValues:{},photos:[],aiEvaluationResult:'',aiEvaluationClause:''})}syncCheck(0)}catch(e){console.error(e)}loading.value=false})
</script>

<style scoped>
.container{padding:20rpx 20rpx 60rpx}.loading{text-align:center;padding:80rpx;color:#626F7D}
.top-bar{display:flex;justify-content:space-between;padding:10rpx 0 20rpx;align-items:center}.nav-btns{display:flex;gap:20rpx}.btn-txt{background:none;border:none;font-size:26rpx;color:#226CB3;padding:0;line-height:1.5}.btn-txt::after{border:none}
.title-row{margin-bottom:24rpx}.title{font-size:36rpx;font-weight:bold;color:#171D26;display:block}.cat{font-size:24rpx;color:#626F7D;margin-top:4rpx;display:block}
.sec{margin-bottom:28rpx}.slabel{display:block;font-size:28rpx;font-weight:bold;color:#171D26;margin-bottom:14rpx}.hint{font-size:24rpx;color:#B0B8C2;padding:20rpx 0}
.ar{display:flex;gap:12rpx;align-items:center;margin-bottom:12rpx}.edit-hint{font-size:24rpx;color:#626F7D;white-space:nowrap;flex-shrink:0}.ai{flex:1;height:64rpx;padding:0 16rpx;background:#EDF0F4;border-radius:8rpx;font-size:26rpx}.btn{border:none;border-radius:8rpx;padding:10rpx 20rpx;font-size:24rpx;white-space:nowrap}.green{background:#2EA65E;color:#fff}
.tabs{display:flex;flex-wrap:wrap;gap:10rpx}.tab{display:flex;align-items:center;gap:6rpx;padding:8rpx 16rpx;background:#EDF0F4;border-radius:8rpx;font-size:24rpx}.tab.on{background:#226CB3;color:#fff}.tax{font-size:20rpx;opacity:.7}.tab-inp{width:120rpx;height:36rpx;padding:0 6rpx;background:rgba(255,255,255,.6);border:1px solid rgba(255,255,255,.8);border-radius:4rpx;font-size:20rpx;text-align:center;color:inherit}.tx{background:none;border:none;font-size:26rpx;color:inherit;padding:0 4rpx;line-height:1}.tx::after{border:none}
.sg{margin-bottom:14rpx}.sgh{display:flex;align-items:center;gap:10rpx;padding:8rpx 12rpx;background:#F5F7FA;border-radius:6rpx}.sd{width:10rpx;height:10rpx;border-radius:50%;flex-shrink:0}.sgt{font-size:25rpx;font-weight:bold;color:#171D26;flex:1}.sgn{font-size:20rpx;color:#626F7D}
.sr{display:flex;padding:10rpx 12rpx;border-bottom:1rpx solid #F5F7FA;gap:10rpx}.scb{background:none;border:none;font-size:30rpx;color:#226CB3;padding:0 4rpx;margin-top:4rpx;flex-shrink:0}.scb::after{border:none}.sb{flex:1}.sdsc{font-size:25rpx;color:#454D59;line-height:1.6}.dci{display:inline-block;width:90rpx;height:40rpx;padding:0 6rpx;background:#fff;border:1px solid #D5DAE0;border-radius:4rpx;font-size:22rpx;text-align:center;margin:0 4rpx;vertical-align:middle}.sm{display:flex;align-items:center;gap:10rpx;margin-top:6rpx}.sbg{font-size:18rpx;color:#fff;padding:2rpx 10rpx;border-radius:4rpx}.scl{font-size:20rpx;color:#626F7D}
.btn-a{background:linear-gradient(135deg,#226CB3,#1B5A96);color:#fff;border:none;border-radius:4rpx;padding:20rpx 0;font-size:28rpx;margin-bottom:12rpx;width:100%}.ac{padding:14rpx;background:#EBF5EE;border-radius:4rpx;font-size:26rpx;margin-top:12rpx}.aclbl{color:#171D26}.av{font-weight:bold;font-size:30rpx}.aclref{font-size:22rpx;color:#626F7D;display:block;margin-top:4rpx}
.btn-s{width:100%;background:#2EA65E;color:#fff;border:none;border-radius:4rpx;padding:24rpx 0;font-size:32rpx;margin-top:20rpx}.btm-nav{display:flex;justify-content:space-between;padding:20rpx 0}
</style>
