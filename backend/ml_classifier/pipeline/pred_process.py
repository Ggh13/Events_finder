import os, json, csv
# from transformers import AutoTokenizer

def pred_process() -> int:
    # tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
    # text_max_len = 0

    os.makedirs("processed/images", exist_ok=True)
    os.makedirs("processed/texts", exist_ok=True)
    main_path = "parser/data"
    res_path = "train_data"
    rows = []

    for channel in os.listdir(main_path):
        channel_path = os.path.join(main_path, channel)
        json_path = os.path.join(channel_path, "posts.json")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for post in data["posts"]:
            post_id = f"{channel}_{post['id']}"

            text_filename = f"texts/{post_id}.txt"
            text_path = os.path.join("processed", text_filename)
            with open (text_path, 'w', encoding='utf-8') as f:
                f.write(post['text'])
            # text_max_len = max(text_max_len, len(tokenizer.tokenize(post['text'])))
            image_path = None
            
            if post['has_image'] == True:
                src_img_path = os.path.join(channel_path, "images", post["img_filename"])
                os.system(f'cp {src_img_path} "processed/images"/{post["img_filename"]}')
                image_path = f"images/{post['img_filename']}"
            
            rows.append(
                {
                    "text_file": text_filename,
                    "image_file": image_path,
                    "has_image": 1 if post['has_image'] else 0,
                    "label": channel
                }
            )
    with open("processed/metadata.csv", "w", encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text_file", "image_file", "label", "has_image"])
        for row in rows:
            writer.writerow([row["text_file"], row["image_file"], row["label"], row["has_image"]])
    # print(text_max_len+10) #574 -> 512 (cause its max for deafult tokenizer)

if __name__ == "__main__":
    pred_process()