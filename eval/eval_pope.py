import json

ans_file = '../output/example/pope/gemini_pope_popular_multi.jsonl'


label_file = '../data/coco_pope_popular.json'


yuan_label_file = '../data/coco_pope_popular.json'


output_file = '../badcase_list/pope_popular_gemini_multi_badcaselist.json'
out = False
all = False

answers = [json.loads(q) for q in open(ans_file, 'r')]
label_list = [json.loads(q)['label'] for q in open(label_file, 'r')]
yuan_label_list = [json.loads(q)['label'] for q in open(yuan_label_file, 'r')]
img_list = [json.loads(q)['image'] for q in open(label_file, 'r')]

badcase_list = []

for answer in answers:
    text = answer['answer']

    if text.find('.') != -1:
        text = text.split('.')[0]

    text = text.replace(',', '')
    words = text.split(' ')
    if 'No' in words or 'not' in words or 'no' in words:
        answer['answer'] = 'no'
    else:
        answer['answer'] = 'yes'



for i in range(len(label_list)):
    if label_list[i] == 'no':
        label_list[i] = 0
    elif label_list[i] == 'yes':
        label_list[i] = 1
    elif label_list[i] == 'uncertain':
        label_list[i] = -1

for i in range(len(yuan_label_list)):
    if yuan_label_list[i] == 'no':
        yuan_label_list[i] = 0
    elif yuan_label_list[i] == 'yes':
        yuan_label_list[i] = 1


pred_list = []
for answer in answers:
    if answer['answer'] == 'no':
        pred_list.append(0)
    else:
        pred_list.append(1)

pos = 1
neg = 0
yes_ratio = pred_list.count(1) / len(pred_list)

TP, TN, FP, FN = 0, 0, 0, 0
question_id = 1
for pred, label in zip(pred_list, label_list):
    kk = {}
    if pred == pos and label == pos:
        TP += 1
    elif pred == pos and label == neg:
        FP += 1
        if out:
            kk['image_id'] = question_id
            kk['image'] = img_list[question_id-1]
            kk['question'] = answers[question_id-1]['question']
            kk['pred'] = answers[question_id-1]['answer']
            kk['label'] = label_list[question_id-1]
            # kk['discussion_process'] = answers[question_id-1]['discussion_process']
            badcase_list.append(kk)
    elif pred == neg and label == neg:
        TN += 1
    elif pred == neg and label == pos:
        FN += 1
        if out:
            kk['image_id'] = question_id
            kk['image'] = img_list[question_id-1]
            kk['question'] = answers[question_id-1]['question']
            kk['pred'] = answers[question_id-1]['answer']
            kk['label'] = label_list[question_id-1]
            # kk['discussion_process'] = answers[question_id-1]['discussion_process']
            badcase_list.append(kk)
    else:
        if all == True and label == -1:
            label = yuan_label_list[question_id-1]
            if pred == pos and label == pos:
                TP += 1
            elif pred == pos and label == neg:
                FP += 1
                if out:
                    kk['image_id'] = question_id
                    kk['image'] = img_list[question_id - 1]
                    kk['question'] = answers[question_id - 1]['question']
                    kk['pred'] = answers[question_id - 1]['answer']
                    kk['label'] = label_list[question_id - 1]
                    # kk['discussion_process'] = answers[question_id - 1]['discussion_process']
                    badcase_list.append(kk)
            elif pred == neg and label == neg:
                TN += 1
            elif pred == neg and label == pos:
                FN += 1
                if out:
                    kk['image_id'] = question_id
                    kk['image'] = img_list[question_id - 1]
                    kk['question'] = answers[question_id - 1]['question']
                    kk['pred'] = answers[question_id - 1]['answer']
                    kk['label'] = label_list[question_id - 1]
                    # kk['discussion_process'] = answers[question_id - 1]['discussion_process']
                    badcase_list.append(kk)

    question_id += 1

if out == True:
    print(badcase_list)
    print(len(badcase_list))
    json.dump(badcase_list, open(output_file, 'w'))


print('TP\tFP\tTN\tFN\t')
print('{}\t{}\t{}\t{}'.format(TP, FP, TN, FN))


acc = (TP + TN) / (TP + TN + FP + FN) 
precision = float(TP) / float(TP + FP) 
recall = float(TP) / float(TP + FN) 
f1 = 2*precision*recall / (precision + recall) 

print('Accuracy: {}'.format(acc))
print('Precision: {}'.format(precision))
print('Recall: {}'.format(recall))
print('F1 score: {}'.format(f1))
print('Yes ratio: {}'.format(yes_ratio))
