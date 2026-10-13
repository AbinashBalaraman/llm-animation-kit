from pathlib import Path
import json, hashlib, math

ROOT = Path(__file__).resolve().parent
EX = ROOT / 'examples'
FIX = EX / 'fixtures'
FIX.mkdir(parents=True, exist_ok=True)

def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')

def ref(name): return {'$ref': '#/$defs/' + name}
def obj(props, required=None, **extras):
    return {'type':'object','properties':props,'required':list(props) if required is None else required,'additionalProperties':False,**extras}
def arr(items, minimum=0, **extras): return {'type':'array','items':items,'minItems':minimum,**extras}
def enum(*vals): return {'type':'string','enum':list(vals)}
def integer(minimum=0): return {'type':'integer','minimum':minimum}
ID = {'type':'string','pattern':'^[a-z][a-z0-9_]{2,63}$'}
TEXT = {'type':'string','minLength':1}
NUM = {'type':'number'}
POS = {'type':'number','exclusiveMinimum':0}
UNIT = {'type':'number','minimum':0,'maximum':1}
RIG = {'const':'rig_humanoid_v1'}
VEC = {'type':'array','items':NUM,'minItems':3,'maxItems':3}
QUAT = {'type':'array','items':NUM,'minItems':4,'maxItems':4,'description':'Unit quaternion x,y,z,w. Normalization is a semantic check.'}
D = {'id':ID}
D['frameRange'] = obj({'start':integer(),'end':integer(1)},description='Scene-local integer frames, zero-based, half-open [start,end). Semantic check: end > start.')
D['transform'] = obj({'positionM':VEC,'rotationXyzw':QUAT,'scale':{'type':'array','items':POS,'minItems':3,'maxItems':3}},description='World space, meters, right-handed Z-up, character forward +Y, except attachment localTransform is parent-socket relative.')
D['assetRef'] = obj({'assetId':ID,'uri':TEXT,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'assetType':enum('character_rig','motion_library','environment','prop','audio'),'rigProfileId':{'oneOf':[RIG,{'type':'null'}]},'mediaType':TEXT,'materialization':enum('synthetic_fixture','production')},description='Hash exact bytes before decoding. URI is project-relative. Rigged assets require selected profile; nonrigged assets use null (semantic check).')
D['localBox'] = obj({'centerM':VEC,'rotationXyzw':QUAT,'halfExtentsM':{'type':'array','items':POS,'minItems':3,'maxItems':3}},description='Box in the owning entity local coordinates. Not a collision mesh.')
D['affordance'] = {'oneOf':[
    obj({'affordanceId':ID,'kind':{'const':'grasp'},'localPositionM':VEC,'localRotationXyzw':QUAT,'allowedEffectors':arr(enum('left_hand','right_hand'),1,uniqueItems=True),'positionToleranceM':POS,'angleToleranceDegrees':{'type':'number','exclusiveMinimum':0,'maximum':180}}),
    obj({'affordanceId':ID,'kind':{'const':'seat'},'localPositionM':VEC,'localRotationXyzw':QUAT,'footZone':ref('localBox'),'clearanceBox':ref('localBox'),'maxOccupants':{'const':1}}),
    obj({'affordanceId':ID,'kind':{'const':'support'},'localPositionM':VEC,'localRotationXyzw':QUAT,'halfExtentsM':{'type':'array','items':POS,'minItems':2,'maxItems':2}})
]}
D['contact'] = obj({'actorId':ID,'effector':enum('left_hand','right_hand','left_foot','right_foot'),'targetEntityId':ID,'affordanceId':ID})
D['ownership'] = obj({'propId':ID,'ownerId':{'oneOf':[ID,{'type':'null'}]}})
D['attachment'] = obj({'propId':ID,'parentEntityId':ID,'parentSocketId':ID,'localTransform':ref('transform')},description='Transform parent, distinct from logical ownership. localTransform is relative to named parent socket.')
D['seatOccupancy'] = obj({'actorId':ID,'seatEntityId':ID,'seatAffordanceId':ID})
D['condition'] = {'oneOf':[
    obj({'conditionType':{'const':'ownership'},'propId':ID,'ownerId':{'oneOf':[ID,{'type':'null'}]}}),
    obj({'conditionType':{'const':'contact'},'actorId':ID,'effector':enum('left_hand','right_hand','left_foot','right_foot'),'targetEntityId':ID,'affordanceId':ID,'active':{'type':'boolean'}}),
    obj({'conditionType':{'const':'hand_free'},'actorId':ID,'hand':enum('left_hand','right_hand')}),
    obj({'conditionType':{'const':'proximity'},'actorId':ID,'targetEntityId':ID,'maxDistanceM':POS}),
    obj({'conditionType':{'const':'seated'},'actorId':ID,'seatEntityId':ID,'seatAffordanceId':ID,'active':{'type':'boolean'}})
]}
D['resourceClaim'] = obj({'entityId':ID,'channels':arr(enum('root','legs','torso','left_arm','right_arm','head','gaze','face','voice'),1,uniqueItems=True)})
D['composition'] = {'oneOf':[obj({'policy':{'const':'exclusive'}}),obj({'policy':{'const':'compatible'},'compatibilityProfileId':ID})]}
D['camera'] = obj({'projection':enum('perspective','orthographic'),'positionM':VEC,'targetM':VEC,'up':{'const':[0,0,1]},'verticalFovDegrees':{'type':'number','exclusiveMinimum':0,'exclusiveMaximum':180},'orthographicHeightM':POS,'nearM':POS,'farM':POS},required=['projection','positionM','targetM','up','nearM','farM'],allOf=[{'if':{'properties':{'projection':{'const':'perspective'}}},'then':{'required':['verticalFovDegrees'],'not':{'required':['orthographicHeightM']}},'else':{'required':['orthographicHeightM'],'not':{'required':['verticalFovDegrees']}}}])
TYPES = ['walk_to','look_at','gesture','speak','handover','sit','expression']
EXPRESSIONS = enum('neutral','happy','sad','angry','surprised','suspicious')
def doc(kind, props, required=None):
    base={'schemaVersion':{'const':'0.1.0'},'documentType':{'const':kind},'projectId':ID,**props}
    return obj(base,None if required is None else ['schemaVersion','documentType','projectId']+required)
D['documentRef'] = obj({'documentId':ID,'documentType':enum('characterRef','scene','shot','action'),'path':{'type':'string','pattern':'^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))[A-Za-z0-9._/-]+$'}})
D['project'] = doc('project',{'revision':integer(),'title':TEXT,'fps':obj({'numerator':integer(1),'denominator':integer(1)}),'audioSampleRateHz':{'const':48000},'coordinates':obj({'lengthUnit':{'const':'meter'},'handedness':{'const':'right'},'up':{'const':'+Z'},'characterForward':{'const':'+Y'},'quaternionOrder':{'const':'xyzw'}}),'frameConvention':{'const':'zero_based_half_open'},'selectedRigProfileId':RIG,'motionLibraryAssetId':ID,'assets':arr(ref('assetRef'),1),'documents':arr(ref('documentRef'),1),'shotOrder':arr(ID,1,uniqueItems=True),'renderProfile':obj({'widthPx':integer(1),'heightPx':integer(1),'colorSpace':{'const':'Rec.709'},'styleProfileId':ID})})
D['characterRef'] = doc('characterRef',{'characterId':ID,'displayName':TEXT,'rigProfileId':RIG,'rigAsset':ref('assetRef'),'appearanceProfileId':ID,'voiceProfileId':ID,'supportedActions':arr(enum(*TYPES),1,uniqueItems=True)})
D['entity'] = {'oneOf':[obj({'entityId':ID,'entityType':{'const':'character'},'characterRefId':ID,'transform':ref('transform')}),obj({'entityId':ID,'entityType':enum('prop','environment'),'assetId':ID,'transform':ref('transform'),'affordances':arr(ref('affordance'))})]}
D['scene'] = doc('scene',{'sceneId':ID,'durationFrames':integer(1),'entities':arr(ref('entity'),1),'initialState':obj({'ownership':arr(ref('ownership')),'contacts':arr(ref('contact')),'attachments':arr(ref('attachment')),'seatOccupancy':arr(ref('seatOccupancy'))}),'actionIds':arr(ID,uniqueItems=True),'lightingProfileId':ID})
D['shot'] = doc('shot',{'shotId':ID,'sceneId':ID,'frameRange':ref('frameRange'),'camera':ref('camera'),'compositionIntent':TEXT,'renderOverrides':obj({'seed':integer()},required=[])},required=['shotId','sceneId','frameRange','camera','compositionIntent'])
PARAMS = {
    'walk_to':obj({'destinationM':VEC,'facingTargetEntityId':ID,'speedMps':POS,'motionAssetId':ID}),
    'look_at':obj({'targetEntityId':ID,'targetAffordanceId':ID,'influence':UNIT,'easeInFrames':integer()},required=['targetEntityId','influence','easeInFrames']),
    'gesture':obj({'gestureId':ID,'hand':enum('left_hand','right_hand','both'),'intensity':UNIT,'motionAssetId':ID}),
    'speak':obj({'text':TEXT,'language':TEXT,'audioAssetId':ID,'audioRangeSamples':obj({'start':integer(),'end':integer(1)}),'visemes':arr(obj({'atSample':integer(),'visemeId':ID,'weight':UNIT}))}),
    'handover':obj({'propId':ID,'receiverId':ID,'giverHand':enum('left_hand','right_hand'),'receiverHand':enum('left_hand','right_hand'),'giverGraspAffordanceId':ID,'receiverGraspAffordanceId':ID,'receiverContactFrame':integer(),'transferFrame':integer(),'giverReleaseFrame':integer(),'style':enum('neutral','hesitant','gentle'),'motionAssetId':ID}),
    'sit':obj({'seatEntityId':ID,'seatAffordanceId':ID,'seatContactFrame':integer(),'motionAssetId':ID}),
    'expression':obj({'expression':EXPRESSIONS,'intensity':UNIT,'easeInFrames':integer(),'easeOutFrames':integer()})
}
for kind in TYPES:
    D['action_'+kind] = doc('action',{'actionId':ID,'sceneId':ID,'actorId':ID,'actionType':{'const':kind},'frameRange':ref('frameRange'),'resourceClaims':arr(ref('resourceClaim'),1),'composition':ref('composition'),'preconditions':arr(ref('condition')),'postconditions':arr(ref('condition')),'parameters':PARAMS[kind]})
D['action'] = {'oneOf':[ref('action_'+kind) for kind in TYPES]}
D['operation'] = {'oneOf':[
    obj({'operationId':ID,'operation':{'const':'shift_action'},'actionId':ID,'deltaFrames':{'type':'integer','not':{'const':0}}}),
    obj({'operationId':ID,'operation':{'const':'set_expression'},'actionId':ID,'expression':EXPRESSIONS,'intensity':UNIT}),
    obj({'operationId':ID,'operation':{'const':'replace_shot_camera'},'shotId':ID,'camera':ref('camera')}),
    obj({'operationId':ID,'operation':{'const':'replace_action'},'actionId':ID,'value':ref('action')}),
    obj({'operationId':ID,'operation':{'const':'add_action'},'sceneId':ID,'value':ref('action')}),
    obj({'operationId':ID,'operation':{'const':'remove_action'},'actionId':ID}),
    obj({'operationId':ID,'operation':{'const':'replace_entity_transform'},'sceneId':ID,'entityId':ID,'value':ref('transform')})
]}
D['revision'] = doc('revision',{'revisionId':ID,'expectedRevision':integer(),'atomic':{'const':True},'intent':TEXT,'operations':arr(ref('operation'),1)})
D['validationIssue'] = obj({'code':{'type':'string','pattern':'^[A-Z][A-Z0-9_]+$'},'severity':enum('error','warning','info'),'document_id':ID,'json_pointer':{'type':'string','pattern':'^(?:|/.*)$'},'message':TEXT,'repair_hint':{'type':['string','null']}})
D['validationReport'] = doc('validationReport',{'reportId':ID,'stage':enum('schema','resolve','semantic','compile','render','review'),'status':enum('passed','failed','not_run'),'issues':arr(ref('validationIssue')),'checksRun':arr(TEXT,uniqueItems=True),'checksNotRun':arr(TEXT,uniqueItems=True)})
D['jobStatus'] = enum('planned','running','succeeded','failed','cancelled')
save(ROOT/'studio.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://schemas.invalid/animation-studio/0.1.0/studio.schema.json','title':'Animation Studio proposed contract bundle v0.1.0','description':'Proposal only. Root accepts one project, characterRef, scene, shot, action, revision, or validationReport document. Not an animation executor.','oneOf':[ref(n) for n in ['project','characterRef','scene','shot','action','revision','validationReport']],'$defs':D})

# Intentionally non-renderable metadata fixtures. Hash the exact saved bytes.
specs=[
    ('asset_aya_rig','character_rig','rig_humanoid_v1',{'label':'Aya rig fixture','sockets':['left_hand','right_hand'],'containsRig':False}),
    ('asset_ren_rig','character_rig','rig_humanoid_v1',{'label':'Ren rig fixture','sockets':['left_hand','right_hand'],'containsRig':False}),
    ('asset_motion_library','motion_library','rig_humanoid_v1',{'label':'Motion catalog fixture','actions':TYPES,'containsAnimationData':False}),
    ('asset_courtyard','environment',None,{'label':'Courtyard fixture','containsGeometry':False}),
    ('asset_table','prop',None,{'label':'Table fixture','containsGeometry':False}),
    ('asset_chair','prop',None,{'label':'Chair fixture','containsGeometry':False}),
    ('asset_cup','prop',None,{'label':'Cup fixture','containsGeometry':False}),
    ('asset_line_aya','audio',None,{'label':'Speech metadata fixture','sampleRateHz':48000,'sampleCount':96000,'text':'Here, take it.','containsAudio':False})
]
assets=[]
for aid,kind,rig,body in specs:
    path=FIX/(aid+'.json')
    save(path,{'fixtureVersion':'0.1.0','synthetic':True,**body})
    assets.append({'assetId':aid,'uri':'fixtures/'+path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'assetType':kind,'rigProfileId':rig,'mediaType':'application/json','materialization':'synthetic_fixture'})
assetmap={a['assetId']:a for a in assets}
PROJECT='project_handover_fixture'
SCENE='scene_courtyard'
def base(kind): return {'schemaVersion':'0.1.0','documentType':kind,'projectId':PROJECT}
def transform(pos,rot=None): return {'positionM':pos,'rotationXyzw':rot or [0,0,0,1],'scale':[1,1,1]}
def rng(a,b): return {'start':a,'end':b}
def contact(actor,hand,grasp): return {'actorId':actor,'effector':hand,'targetEntityId':'prop_cup','affordanceId':grasp}
def ownership(owner): return {'conditionType':'ownership','propId':'prop_cup','ownerId':owner}
def cc(actor,hand,grasp,active=True): return {'conditionType':'contact',**contact(actor,hand,grasp),'active':active}
for name in ['aya','ren']:
    save(EX/('character-'+name+'.json'),{**base('characterRef'),'characterId':'char_'+name,'displayName':name.capitalize(),'rigProfileId':'rig_humanoid_v1','rigAsset':assetmap['asset_'+name+'_rig'],'appearanceProfileId':'appearance_'+name+'_v1','voiceProfileId':'voice_'+name+'_v1','supportedActions':TYPES})
q=math.sqrt(0.5)
scene={**base('scene'),'sceneId':SCENE,'durationFrames':480,'entities':[
    {'entityId':'char_aya','entityType':'character','characterRefId':'char_aya','transform':transform([0,0,0],[0,0,-q,q])},
    {'entityId':'char_ren','entityType':'character','characterRefId':'char_ren','transform':transform([1.8,0,0],[0,0,q,q])},
    {'entityId':'env_courtyard','entityType':'environment','assetId':'asset_courtyard','transform':transform([0,0,0]),'affordances':[]},
    {'entityId':'prop_table','entityType':'prop','assetId':'asset_table','transform':transform([0.8,1.6,0]),'affordances':[{'affordanceId':'table_surface','kind':'support','localPositionM':[0,0,0.75],'localRotationXyzw':[0,0,0,1],'halfExtentsM':[0.5,0.35]}]},
    {'entityId':'prop_chair','entityType':'prop','assetId':'asset_chair','transform':transform([1.4,-0.5,0]),'affordances':[{'affordanceId':'chair_seat','kind':'seat','localPositionM':[0,0,0.45],'localRotationXyzw':[0,0,0,1],'footZone':{'centerM':[0,0.4,0.05],'rotationXyzw':[0,0,0,1],'halfExtentsM':[0.3,0.25,0.05]},'clearanceBox':{'centerM':[0,0.25,0.9],'rotationXyzw':[0,0,0,1],'halfExtentsM':[0.5,0.7,0.9]},'maxOccupants':1}]},
    {'entityId':'prop_cup','entityType':'prop','assetId':'asset_cup','transform':transform([0.35,0,1]),'affordances':[{'affordanceId':'cup_handle','kind':'grasp','localPositionM':[0.05,0,0],'localRotationXyzw':[0,0,0,1],'allowedEffectors':['right_hand'],'positionToleranceM':0.005,'angleToleranceDegrees':5},{'affordanceId':'cup_body','kind':'grasp','localPositionM':[0,0,0],'localRotationXyzw':[0,0,0,1],'allowedEffectors':['left_hand'],'positionToleranceM':0.005,'angleToleranceDegrees':5}]}
],'initialState':{'ownership':[{'propId':'prop_table','ownerId':None},{'propId':'prop_chair','ownerId':None},{'propId':'prop_cup','ownerId':'char_aya'}],'contacts':[contact('char_aya','right_hand','cup_handle')],'attachments':[{'propId':'prop_cup','parentEntityId':'char_aya','parentSocketId':'right_hand','localTransform':transform([0,0,0])}],'seatOccupancy':[]},'actionIds':['act_walk','act_look','act_gesture','act_speak','act_handover','act_expression','act_sit'],'lightingProfileId':'lighting_courtyard_soft_v1'}
save(EX/'scene.json',scene)
cam_a={'projection':'perspective','positionM':[3.4,-5,2.2],'targetM':[0.7,0,1.1],'up':[0,0,1],'nearM':0.1,'farM':100,'verticalFovDegrees':40}
cam_b={'projection':'perspective','positionM':[3,-2.6,1.5],'targetM':[1,0,1.1],'up':[0,0,1],'nearM':0.1,'farM':100,'verticalFovDegrees':34}
for suffix,fr,cam,intent in [('a',rng(0,240),cam_a,'Establish the characters and show the cup transfer clearly.'),('b',rng(240,480),cam_b,'Hold on Ren taking a seat with the same cup after the cut.')]:
    save(EX/('shot-'+suffix+'.json'),{**base('shot'),'shotId':'shot_offer_'+suffix,'sceneId':SCENE,'frameRange':fr,'camera':cam,'compositionIntent':intent})
def action(name,kind,actor,a,b,claims,params,pre=None,post=None):
    value={**base('action'),'actionId':'act_'+name,'sceneId':SCENE,'actorId':actor,'actionType':kind,'frameRange':rng(a,b),'resourceClaims':[{'entityId':eid,'channels':channels} for eid,channels in claims],'composition':{'policy':'exclusive'},'preconditions':pre or [],'postconditions':post or [],'parameters':params}
    save(EX/('action-'+name+'.json'),value)
    return value
M='asset_motion_library'
actions=[
    action('walk','walk_to','char_ren',0,96,[('char_ren',['root','legs','torso','left_arm','right_arm'])],{'destinationM':[0.8,0,0],'facingTargetEntityId':'char_aya','speedMps':0.25,'motionAssetId':M}),
    action('look','look_at','char_aya',96,240,[('char_aya',['gaze'])],{'targetEntityId':'char_ren','influence':1,'easeInFrames':8}),
    action('gesture','gesture','char_aya',96,132,[('char_aya',['left_arm'])],{'gestureId':'gesture_open_palm','hand':'left_hand','intensity':0.6,'motionAssetId':M}),
    action('speak','speak','char_aya',108,156,[('char_aya',['voice','face'])],{'text':'Here, take it.','language':'en','audioAssetId':'asset_line_aya','audioRangeSamples':{'start':0,'end':96000},'visemes':[{'atSample':0,'visemeId':'viseme_rest','weight':0},{'atSample':8000,'visemeId':'viseme_aa','weight':0.7},{'atSample':40000,'visemeId':'viseme_ee','weight':0.6},{'atSample':92000,'visemeId':'viseme_rest','weight':0}]}),
    action('handover','handover','char_aya',144,216,[('char_aya',['right_arm','torso']),('char_ren',['left_arm','torso'])],{'propId':'prop_cup','receiverId':'char_ren','giverHand':'right_hand','receiverHand':'left_hand','giverGraspAffordanceId':'cup_handle','receiverGraspAffordanceId':'cup_body','receiverContactFrame':176,'transferFrame':180,'giverReleaseFrame':184,'style':'gentle','motionAssetId':M},pre=[ownership('char_aya'),cc('char_aya','right_hand','cup_handle'),{'conditionType':'hand_free','actorId':'char_ren','hand':'left_hand'},{'conditionType':'proximity','actorId':'char_aya','targetEntityId':'char_ren','maxDistanceM':1.2}],post=[ownership('char_ren'),cc('char_ren','left_hand','cup_body'),cc('char_aya','right_hand','cup_handle',False)]),
    action('expression','expression','char_ren',184,240,[('char_ren',['face'])],{'expression':'happy','intensity':0.6,'easeInFrames':8,'easeOutFrames':8}),
    action('sit','sit','char_ren',264,336,[('char_ren',['root','legs','torso','left_arm','right_arm'])],{'seatEntityId':'prop_chair','seatAffordanceId':'chair_seat','seatContactFrame':304,'motionAssetId':M},pre=[ownership('char_ren'),{'conditionType':'proximity','actorId':'char_ren','targetEntityId':'prop_chair','maxDistanceM':1}],post=[ownership('char_ren'),cc('char_ren','left_hand','cup_body'),{'conditionType':'seated','actorId':'char_ren','seatEntityId':'prop_chair','seatAffordanceId':'chair_seat','active':True}])
]
docs=[{'documentId':'char_'+n,'documentType':'characterRef','path':'character-'+n+'.json'} for n in ['aya','ren']]
docs += [{'documentId':SCENE,'documentType':'scene','path':'scene.json'}]
docs += [{'documentId':'shot_offer_'+s,'documentType':'shot','path':'shot-'+s+'.json'} for s in ['a','b']]
docs += [{'documentId':a['actionId'],'documentType':'action','path':'action-'+a['actionId'][4:]+'.json'} for a in actions]
save(EX/'project.json',{**base('project'),'revision':7,'title':'Synthetic courtyard handover contract fixture','fps':{'numerator':24,'denominator':1},'audioSampleRateHz':48000,'coordinates':{'lengthUnit':'meter','handedness':'right','up':'+Z','characterForward':'+Y','quaternionOrder':'xyzw'},'frameConvention':'zero_based_half_open','selectedRigProfileId':'rig_humanoid_v1','motionLibraryAssetId':M,'assets':assets,'documents':docs,'shotOrder':['shot_offer_a','shot_offer_b'],'renderProfile':{'widthPx':1280,'heightPx':720,'colorSpace':'Rec.709','styleProfileId':'style_cel_fixture_v1'}})
save(EX/'revision.json',{**base('revision'),'revisionId':'revision_delay_handover','expectedRevision':7,'atomic':True,'intent':'Delay the handover and corresponding facial reaction by one second. Keep cameras unchanged.','operations':[{'operationId':'op_shift_handover','operation':'shift_action','actionId':'act_handover','deltaFrames':24},{'operationId':'op_shift_expression','operation':'shift_action','actionId':'act_expression','deltaFrames':24}]})
save(EX/'validation-report.json',{**base('validationReport'),'reportId':'report_fixture_schema','stage':'schema','status':'passed','issues':[{'code':'SYNTHETIC_FIXTURE_ASSETS','severity':'warning','document_id':PROJECT,'json_pointer':'/assets','message':'Assets are synthetic JSON fixture bytes, not renderable geometry, rigs, motion, or audio.','repair_hint':'Replace fixtures with licensed production assets; rerun all later validation stages.'}],'checksRun':['JSON Schema Draft 2020-12 example validation'],'checksNotRun':['Geometry, rig, motion, and audio decoding','Physical contact and reachability','Compilation, rendering, and visual quality']})
print('Created schema, 15 example documents, and 8 synthetic fixture assets.')
