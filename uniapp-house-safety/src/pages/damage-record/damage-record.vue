<template>
  <view class="container">
    <view class="bar"><button class="btn-txt" @click="goBack">← 返回数据采集</button></view>

    <!-- 分类筛选 -->
    <view class="fb">
      <view v-for="c in cats" :key="c" class="fi" :class="{on:af===c}" @click="af=c">
        <text>{{c}} ({{catCounts[c]||0}})</text>
      </view>
    </view>

    <!-- 构件类型列表 -->
    <block v-if="filteredTypes.length>0">
      <view v-for="ct in filteredTypes" :key="ct.type" class="tc">
        <view class="th" @click="goInspect(ct.type)">
          <view class="ti"><text class="tn">{{ct.type}}</text><text class="tcat">{{ct.category}}</text></view>
          <view class="tr"><text class="tcnt">{{ct.checks.length}}个</text><text v-if="ct.worstResult" class="rb" :style="{background:getColor(ct.worstResult)}">{{ct.worstResult}}</text><text class="ta">▶</text></view>
        </view>
        <view class="axr" v-if="ct.checks.length>0">
          <view v-for="(c,i) in ct.checks" :key="c.id||i" class="axp"><text>{{c.axisLine||c.axis_line||'未标轴号'}}</text></view>
        </view>
        <view class="tf">
          <text v-if="ct.standardsCount>0" class="st">已选 {{ct.standardsCount}} 项标准</text>
          <text v-if="ct.photosCount>0" class="st">{{ct.photosCount}} 张照片</text>
        </view>
        <view class="ta2"><button class="bdt" @click.stop="delType(ct)">删除此类型全部构件</button></view>
      </view>
    </block>

    <view v-else class="es"><text class="ei">+</text><text class="et">暂无构件检查记录</text><text class="eh">请点击下方按钮添加构件类型</text><button class="bea" @click="st=true">选择构件类型</button></view>

    <button class="fab" @click="st=true">+ 添加构件</button>

    <!-- 树形弹窗 -->
    <view v-if="st" class="mm" @click.self="st=false">
      <view class="mc">
        <!-- 标题栏 -->
        <view class="mh">
          <text class="mt">构件目录选择</text>
          <button class="bc" @click="st=false;treePick=[]">×</button>
        </view>
        <text class="mh-hint">按目录勾选，上一级选中则下级全部选中</text>

        <!-- 树形列表 -->
        <scroll-view class="db" scroll-y>
          <block v-for="c in catalog" :key="c.k">
            <!-- 一级：分类 -->
            <view class="tr0" @click="toggleExpand(c.k)">
              <text class="tar">{{treeExp.has(c.k)?'▼':'▶'}}</text>
              <view class="cb" :class="{on:catChk(c)===1,part:catChk(c)===2}" @click.stop="toggleCat(c)">
                <text v-if="catChk(c)===1">✓</text><text v-if="catChk(c)===2">─</text>
              </view>
              <text class="tl0">{{c.l}}</text>
            </view>
            <!-- 子项 -->
            <view v-if="treeExp.has(c.k)">
              <block v-for="s in c.cc" :key="s.k">
                <!-- 有子级：二级分组 -->
                <block v-if="s.cc&&s.cc.length">
                  <view class="tr1" @click="toggleExpand(s.k)">
                    <text class="tar">{{treeExp.has(s.k)?'▼':'▶'}}</text>
                    <view class="cb" :class="{on:subChk(s,c.k)===1,part:subChk(s,c.k)===2}" @click.stop="toggleSub(s,c.k)">
                      <text v-if="subChk(s,c.k)===1">✓</text><text v-if="subChk(s,c.k)===2">─</text>
                    </view>
                    <text class="tl1">{{s.l}}</text>
                  </view>
                  <!-- 三级：叶子 -->
                  <view v-if="treeExp.has(s.k)">
                    <view v-for="l in s.cc" :key="l.k" class="tr2" @click="toggleLeaf(c.k,l.k)">
                      <text class="tdt">•</text>
                      <view class="cb" :class="{on:leafChk(c.k,l.k)}" @click.stop="toggleLeaf(c.k,l.k)">
                        <text v-if="leafChk(c.k,l.k)">✓</text>
                      </view>
                      <text class="tl2">{{l.l}}</text>
                    </view>
                  </view>
                </block>
                <!-- 无子级：直接叶子（二级） -->
                <view v-else class="tr1" @click="toggleLeaf(c.k,s.k)">
                  <text class="tdt">•</text>
                  <view class="cb" :class="{on:leafChk(c.k,s.k)}" @click.stop="toggleLeaf(c.k,s.k)">
                    <text v-if="leafChk(c.k,s.k)">✓</text>
                  </view>
                  <text class="tl1">{{s.l}}</text>
                </view>
              </block>
            </view>
          </block>
        </scroll-view>

        <!-- 已选提示 + 按钮 -->
        <view class="df">
          <text v-if="treePick.length>0" class="df-hint">已选择 {{treePick.length}} 项</text>
          <text v-else class="df-hint"></text>
          <button class="bcc" @click="st=false;treePick=[]">取消</button>
          <button class="bcf" :disabled="treePick.length===0" @click="confirmAdd">确认添加</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getComponentCheckList, createComponentCheck, deleteComponentCheck, getEvaluationStandards } from '@/api/damage-component.js'

const sid = ref('')
const all = ref([])
const stds = ref([])
const af = ref('全部')
const cats = ['地基基础','上部承重结构','围护结构','其他']

	// ---- Catalog-based type ordering (matches tree dialog display order) ----
	function getCatalogOrder() {
	  const order = []
	  for (const cat of catalog) {
	    for (const item of cat.cc) {
	      if (item.cc && item.cc.length) {
	        for (const leaf of item.cc) order.push(leaf.k)
	      } else {
	        order.push(item.k)
	      }
	    }
	  }
	  return order
	}

const catCounts = computed(() => { const m={}; all.value.forEach(c=>{const k=getCat(c);m[k]=(m[k]||0)+1}); return m })

const filteredTypes = computed(() => {
  const m={}
  all.value.forEach(c=>{
    if(af.value!=='全部'&&getCat(c)!==af.value)return
    const t=c.componentType||c.name||c.component_type||'未知'
    if(!m[t])m[t]={type:t,category:getCat(c),checks:[]}
    m[t].checks.push(c)
  })
  const tOrder = getCatalogOrder()
  return Object.values(m).sort((a,b)=>tOrder.indexOf(a.type)-tOrder.indexOf(b.type)).map(ct=>{
    let sc=0,pc=0,wr=''
    const pri={处于危险状态:5,危险状态:5,危险点:5,严重损坏:4,一般损坏:3,'地基稳定，但上部结构倾斜存在安全隐患':3,基本完好:2,非危险状态:1,完好:1}
    ct.checks.forEach(c=>{sc+=(c.checkedItemIds||c.checked_item_ids||[]).length;pc+=(c.photos||[]).length;const r=c.aiEvaluationResult||c.ai_evaluation_result;if(r&&(pri[r]||0)>(pri[wr]||0))wr=r})
    return{...ct,standardsCount:sc,photosCount:pc,worstResult:wr}
  })
})

// ---- Helpers ----
function getCat(c){const t=c.componentType||c.name||c.component_type||'';return['混凝土柱','砖柱','砖墙','混凝土梁','混凝土板','屋架'].includes(t)?'上部承重结构':['砌体自承重墙','承担水平荷载的填充墙','门窗洞口过梁','挑梁','雨棚板','女儿墙'].includes(t)?'围护结构':['地基','基础'].includes(t)?'地基基础':'其他'}
function getColor(r){return({'完好':'#2EA65E','非危险状态':'#2EA65E','基本完好':'#226CB3','一般损坏':'#E28A13','严重损坏':'#D43535','处于危险状态':'#D43535','危险状态':'#D43535','危险点':'#D43535','危险':'#D43535'})[r]||'#626F7D'}

// ---- Catalog ----
const catalog = [
  {k:'地基基础',l:'地基基础',cc:[{k:'地基',l:'地基'},{k:'基础',l:'基础'}]},
  {k:'上部承重结构',l:'上部构件',cc:[{k:'柱构件',l:'柱构件',cc:[{k:'混凝土柱',l:'混凝土柱'},{k:'砖柱',l:'砖柱'}]},{k:'墙构件',l:'墙构件 砖墙',cc:[{k:'砖墙',l:'砖墙'}]},{k:'梁构件',l:'梁构件 混凝土梁',cc:[{k:'混凝土梁',l:'混凝土梁'}]},{k:'板构件',l:'板构件 混凝土板',cc:[{k:'混凝土板',l:'混凝土板'}]},{k:'屋架',l:'屋架'}]},
  {k:'围护结构',l:'围护结构 承重构件',cc:[{k:'砌体自承重墙',l:'砌体自承重墙'},{k:'承担水平荷载的填充墙',l:'承担水平荷载的填充墙'},{k:'门窗洞口过梁',l:'门窗洞口过梁'},{k:'挑梁',l:'挑梁'},{k:'雨棚板',l:'雨棚板'},{k:'女儿墙',l:'女儿墙'}]},
  {k:'其他',l:'其他',cc:[{k:'楼地面',l:'楼地面'},{k:'屋面',l:'屋面'},{k:'非承重墙',l:'非承重墙'},{k:'门窗',l:'门窗'},{k:'外抹灰',l:'外抹灰'},{k:'内抹灰',l:'内抹灰'},{k:'顶棚',l:'顶棚'},{k:'细木装修',l:'细木装修'},{k:'水卫',l:'水卫'},{k:'电照',l:'电照'},{k:'暖气',l:'暖气'},{k:'特种设备',l:'特种设备'}]}
]

// ---- Tree dialog state ----
const st = ref(false)
const treeExp = ref(new Set(['地基基础','上部承重结构','围护结构','其他']))
const treePick = ref([])

function toggleExpand(k){const s=new Set(treeExp.value);s.has(k)?s.delete(k):s.add(k);treeExp.value=s}
function toggleLeaf(c,l){const k=c+'/'+l;const a=[...treePick.value];const i=a.indexOf(k);i>-1?a.splice(i,1):a.push(k);treePick.value=a}
function leafChk(c,l){return treePick.value.includes(c+'/'+l)}
function getLeafs(item,ck){const p=[];if(item.cc)item.cc.forEach(c=>{if(c.cc&&c.cc.length)c.cc.forEach(l=>p.push((ck||item.k)+'/'+l.k));else p.push((ck||item.k)+'/'+c.k)});else p.push((ck||item.k)+'/'+item.k);return p}
function catChk(cat){const ps=getLeafs(cat,cat.k);const c=ps.filter(p=>treePick.value.includes(p)).length;return c===0?0:c===ps.length?1:2}
function subChk(sub,ck){const ps=sub.cc?sub.cc.map(l=>ck+'/'+l.k):[ck+'/'+sub.k];const c=ps.filter(p=>treePick.value.includes(p)).length;return c===0?0:c===ps.length?1:2}
function toggleCat(item){const ps=getLeafs(item,item.k);const all2=ps.every(p=>treePick.value.includes(p));const a=[...treePick.value];if(all2)ps.forEach(p=>{const i=a.indexOf(p);if(i>-1)a.splice(i,1)});else ps.forEach(p=>{if(!a.includes(p))a.push(p)});treePick.value=a}
function toggleSub(sub,ck){const ps=sub.cc?sub.cc.map(l=>ck+'/'+l.k):[ck+'/'+sub.k];const all2=ps.every(p=>treePick.value.includes(p));const a=[...treePick.value];if(all2)ps.forEach(p=>{const i=a.indexOf(p);if(i>-1)a.splice(i,1)});else ps.forEach(p=>{if(!a.includes(p))a.push(p)});treePick.value=a}

// ---- Actions ----
async function confirmAdd(){
  const items=[...new Set(treePick.value)].map(p=>{const[c,l]=p.split('/');return{category:c,componentType:l}})
  try{
    for(const it of items){await createComponentCheck({name:it.componentType,category:it.category,survey_id:sid.value})}
    st.value=false;treePick.value=[]
    await load()
    uni.showToast({title:'已添加'+items.length+'个构件',icon:'success'})
  }catch(e){uni.showToast({title:'添加失败',icon:'none'})}
}
function delType(ct){uni.showModal({title:'确认删除',content:'确定删除"'+ct.type+'"的所有构件？',success:async r=>{if(!r.confirm)return;try{for(const c of ct.checks){if(c.id)try{await deleteComponentCheck(c.id)}catch(e){}};await load();uni.showToast({title:'已删除',icon:'success'})}catch(e){uni.showToast({title:'删除失败',icon:'none'})}}})}
function goInspect(type){uni.navigateTo({url:'/pages/component-inspect/component-inspect?surveyId='+sid.value+'&type='+encodeURIComponent(type)})}
function goBack(){uni.navigateBack()}

onLoad(async o=>{sid.value=o?.id||'';await load()})
async function load(){try{const[r1,r2]=await Promise.all([getComponentCheckList(sid.value),getEvaluationStandards()]);all.value=r1.items||r1||[];stds.value=r2.items||r2||[]}catch(e){}}
</script>

<style scoped>
.container{padding:16rpx 16rpx 140rpx}.bar{padding:10rpx 0 16rpx}.btn-txt{background:none;border:none;font-size:26rpx;color:#226CB3;padding:0}.btn-txt::after{border:none}
.fb{display:flex;gap:10rpx;padding:12rpx 0;overflow-x:auto}.fi{padding:10rpx 20rpx;background:#EDF0F4;border-radius:20rpx;font-size:24rpx;color:#454D59;white-space:nowrap}.fi.on{background:#226CB3;color:#fff}
.tc{background:#fff;border-radius:4rpx;padding:20rpx;box-shadow:0 2rpx 12rpx rgba(0,0,0,.01);margin-bottom:14rpx}
.th{display:flex;justify-content:space-between}.ti{display:flex;flex-direction:column}.tn{font-size:30rpx;font-weight:bold;color:#171D26}.tcat{font-size:22rpx;color:#626F7D}.tr{display:flex;align-items:center;gap:10rpx}.tcnt{font-size:24rpx;color:#626F7D}.rb{font-size:20rpx;color:#fff;padding:4rpx 12rpx;border-radius:4rpx}.ta{font-size:24rpx;color:#B0B8C2}
.axr{display:flex;flex-wrap:wrap;gap:8rpx;margin-top:12rpx}.axp{padding:6rpx 14rpx;background:#E3EDF6;border-radius:6rpx;font-size:22rpx;color:#226CB3}.tf{display:flex;gap:20rpx;margin-top:10rpx}.st{font-size:22rpx;color:#626F7D}
.ta2{margin-top:10rpx;padding-top:10rpx;border-top:1rpx solid #EDF0F4}.bdt{background:none;border:none;font-size:22rpx;color:#D43535;padding:0}.bdt::after{border:none}
.es{text-align:center;padding:120rpx 0}.ei{font-size:80rpx;color:#B0B8C2;display:block;margin-bottom:20rpx}.et{font-size:32rpx;color:#626F7D;margin-bottom:8rpx;display:block}.eh{font-size:24rpx;color:#B0B8C2;margin-bottom:24rpx;display:block}.bea{background:#226CB3;color:#fff;border:none;border-radius:4rpx;padding:22rpx 50rpx;font-size:30rpx}
.fab{position:fixed;bottom:40rpx;left:50%;transform:translateX(-50%);background:#226CB3;color:#fff;border:none;border-radius:50rpx;padding:24rpx 60rpx;font-size:30rpx;box-shadow:0 4rpx 16rpx rgba(34,108,179,.15);z-index:10}
.mm{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:flex;align-items:flex-end;z-index:999}
.mc{width:100%;max-height:85vh;background:#fff;border-radius:24rpx 24rpx 0 0;display:flex;flex-direction:column}
/* 标题栏 */
.mh{display:flex;align-items:center;justify-content:space-between;padding:28rpx 30rpx 16rpx}.mt{font-size:34rpx;font-weight:bold;color:#171D26}.bc{background:none;border:none;font-size:44rpx;color:#626F7D;padding:0;line-height:1;width:60rpx;height:60rpx;display:flex;align-items:center;justify-content:center}.mh-hint{font-size:22rpx;color:#626F7D;padding:0 30rpx 20rpx;display:block}
/* 滚动区 */
.db{flex:1;overflow-y:auto;padding:0 20rpx}
/* 树形行 - 通用 */
.tr0,.tr1,.tr2{display:flex;align-items:center;gap:6rpx;min-height:80rpx;padding:0 16rpx;border-radius:8rpx}.tr0:active,.tr1:active,.tr2:active{background:#EDF0F4}
.tr0{padding-left:8rpx}.tr1{padding-left:44rpx}.tr2{padding-left:80rpx}
/* 展开箭头 */
.tar{font-size:20rpx;color:#626F7D;width:36rpx;height:36rpx;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.tdt{font-size:16rpx;color:#B0B8C2;width:36rpx;text-align:center;flex-shrink:0}
/* 标签文字 */
.tl0{font-size:28rpx;font-weight:bold;color:#171D26;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tl1{font-size:26rpx;color:#454D59;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tl2{font-size:26rpx;color:#454D59;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
/* 复选框 */
.cb{width:38rpx;height:38rpx;border-radius:8rpx;border:2rpx solid #D5DAE0;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:24rpx;color:#fff;background:#fff}.cb.on{background:#226CB3;border-color:#226CB3}.cb.part{background:#A3C5E8;border-color:#226CB3}.cb.part text{color:#fff;font-size:18rpx}
/* 底部操作栏 */
.df{display:flex;align-items:center;gap:20rpx;padding:16rpx 20rpx;border-top:1rpx solid #DBDFE4}.df-hint{font-size:24rpx;color:#226CB3;flex:1}.bcc{flex:1;background:#EDF0F4;color:#454D59;border:none;border-radius:4rpx;padding:22rpx 0;font-size:28rpx;max-width:160rpx}.bcf{flex:1;background:#226CB3;color:#fff;border:none;border-radius:4rpx;padding:22rpx 0;font-size:28rpx;max-width:220rpx}.bcf[disabled]{background:#A3C5E8}
</style>
