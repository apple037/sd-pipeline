## 圖庫存放方式

1. Name: 主目錄以名稱命名
   1. Casey
   2. Lynn
   3. Teresa
   4. Olivia
   5. Rebecca
2. Category: 子目錄
    1. nation: 國籍
    2. style: 風格
    3. age: 年齡
    4. personality: 個性
    5. food: 食物
    6. hobby: 興趣
    7. outfit: 服裝

## MongoDB

1. auto_avatar_config -> 存放設定檔

```json
{
  "name": "Casey",
  "category": [
    "dance",
    "music",
    "cosmetic"
  ]
}
```

2. auto_category_config -> 存放各個分類的prompt

```json
{
  "category": "hobby",
  "name": "Casey",
  "prompt": [
    "guitar",
    "singing",
    "composing"
  ]
}
```

3. job -> 存放自動產圖任務

```json
{
  "_id": {
    "$oid": "64900d178301479f454acfe4"
  },
  "name_list": [
    "Casey",
    "Lynn"
  ],
  "prompt_count": 1,
  "count": 1,
  "width": 512,
  "height": 512,
  "to_gcp": true,
  "status": "finished",
  "created_at": "2023-06-19 16:08:55",
  "updated_at": "2023-06-19 16:09:13",
  "progress": 2
}
```

4. auto_generated_image_detail -> 存放自動產圖詳情

```json
{
  "_id": {
    "$oid": "648ff2e9bedc1e9f1ec0a123"
  },
  "name": "Casey",
  "path": "./outputs/Casey/dance/2023-06-19/cf6f07b6-8211-4bec-a799-5ea96e59d03f.png",
  "prompts": "(half length:1.5), (photorealistic:1.4),8k,(masterpiece), best quality, highest quality, (detailed face:1.5),original,highres, unparalleled masterpiece, ultra realistic 8k,breaking,<lora:Casey666:0.8>",
  "negative_prompts": "logo,text,ng_deepnegative_v1_75t, bad-hands-5, EasyNegative, (worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), watermark,easynegative, paintings, (other hands:1.5), sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans,extra fingers,fewer fingers,strange fingers,bad hand,bad eyes,missing legs,extra arms, ((extra legs:1.5)),extra toes,extra limbs,extra vaginal,bad vaginal,Futanari,ugly, fat, anorexic, blur, warping, grayscale, necklace, (piercings), innie, mirror, DAZ 3D, anime, animated, holding, contortion, warped body, spun around,canvas frame, cartoon, 3d, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), wierd colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly))",
  "created_at": "2023-06-19 14:17:13",
  "used_time": 29.201370000839233
}
```

## 可用接口

### 文生圖

- Path: ```/txt2img```
- Example request:

```json
{
  "name_list": [
    "Casey",
    "Lynn"
  ],
  "prompt_count": 1,
  "count": 1,
  "width": 512,
  "height": 512,
  "to_gcp": true
}
```

- 參數說明
    - name_list: 要生成的人名
    - prompt_count: 每個人要生成的prompt數量
    - count: 每個prompt要生成的圖片數量
    - width: 圖片寬度
    - height: 圖片高度
    - to_gcp: 是否要上傳到gcp

### 取得進程

- Path: ```/running```
- Example response

```json
{
  "jobs": [
    {
      "id": "64900dbf88850f8447588996",
      "count": 1,
      "progress": 0
    }
  ]
}
```

- 參數說明
    - id: 進程id
    - count: 該進程要生成的圖片數量
    - progress: 已完成進度