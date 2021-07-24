# *encoding=utf-8
import os
import argparse
import numpy as np
import pandas as pd

import utils


# judge the subjects if qualified
def analyze_subject(pugcq, golden):
    file_num = len(pugcq)
    subject_list = []
    keys = ["mean", "max_chosen_percent", "srocc", "plcc", "std", "mae", "valid"]
    result_dict = {}
    for key in keys:
        result_dict[key] = []

    for i in range(len(pugcq.keys())):
        if pugcq.keys()[i].find("@") < 0:
            continue
        subject = pugcq.keys()[i]
        subject_list.append(subject)

        # compare with golden
        pugcq_subject = pugcq.iloc[:, i]
        pugcq_subject_sub = pugcq_subject.loc[golden.index]
        pugcq_subject_sub = pugcq_subject_sub.sort_index()
        srocc, plcc = utils.cal_cc(golden, pugcq_subject_sub)
        srocc = 0 if np.isnan(srocc) else srocc
        plcc = 0 if np.isnan(plcc) else plcc
        std = np.sqrt(np.mean(np.square(pugcq_subject_sub - golden)))
        mae = np.mean(np.abs(pugcq_subject_sub - golden))

        # calculate max_chosen_percent in all videos
        max_chosen_num = pugcq_subject.value_counts().values[0]
        max_chosen_percent = max_chosen_num / file_num

        # restore result
        valid = (srocc > 0.6) and (max_chosen_percent < 0.5)
        result_dict[keys[0]].append(pugcq_subject.mean())
        result_dict[keys[1]].append(max_chosen_percent)
        result_dict[keys[2]].append(srocc)
        result_dict[keys[3]].append(plcc)
        result_dict[keys[4]].append(std)
        result_dict[keys[5]].append(mae)
        result_dict[keys[6]].append(valid)

    result_df = pd.DataFrame(result_dict, index=subject_list)
    return result_df


# get mos with filter rule
def handle(pugcq_excel, golden_excel, output_dir="temp"):
    sheet_name_list = pd.ExcelFile(pugcq_excel).sheet_names
    OVERALL = "overall"

    # create output writer
    file_name = utils.get_file_name(pugcq_excel, False)
    utils.check_dir(output_dir)
    output_subject = os.path.join(output_dir, file_name + "_subject_analysis.xls")
    subject_writer = pd.ExcelWriter(output_subject)
    output_filter_mos = os.path.join(output_dir, file_name + "_filter_mos.xls")
    filter_mos_writer = pd.ExcelWriter(output_filter_mos)

    # judge the subjects if qualified
    golden = pd.read_excel(golden_excel, index_col=0)
    golden = golden.sort_index()
    pugcq = pd.read_excel(pugcq_excel, sheet_name=OVERALL, index_col=0).drop("mos", axis=1)
    subject_df = analyze_subject(pugcq, golden[OVERALL])
    subject_df.to_excel(subject_writer, sheet_name=OVERALL, float_format="%0.2f")
    subject_writer.save()

    # drop invalid subject
    subject_valid = subject_df[subject_df["valid"]].index
    print("invalid subject =", subject_df[~subject_df["valid"]].index.to_list())
    pugcq_valid = pugcq[subject_valid]
    mos_valid = pugcq_valid.mean(1)
    pugcq_valid["mos_valid"] = mos_valid

    # quartile filter
    mos_quartile_list = []
    for i in range(0, len(pugcq_valid)):
        scores = pugcq_valid.iloc[i]
        scores_list = list(scores)
        scores_list.sort()
        quartile_1 = scores_list[len(scores_list) // 4]
        quartile_3 = scores_list[len(scores_list) * 3 // 4]
        IQR = [quartile_1 - (quartile_3 - quartile_1) * 1.5, quartile_3 + (quartile_3 - quartile_1) * 1.5]

        valid = (scores >= IQR[0]) & (scores <= IQR[1])
        pugcq_valid.loc[pugcq_valid.index[i], ~valid] = 0
        mos_quartile = scores[valid].mean()
        mos_quartile_list.append(mos_quartile)

    pugcq_valid["mos_quartile"] = mos_quartile_list
    pugcq_valid.to_excel(filter_mos_writer, sheet_name=OVERALL, float_format="%0.2f")
    filter_mos_writer.save()

    # combine mos of each dim
    mos_df = pd.DataFrame(index=pugcq.index)
    mos_df["overall_quartile"] = mos_quartile_list
    mos_df["overall_valid_subject"] = mos_valid
    for name in sheet_name_list:
        mos_df[name] = pd.read_excel(pugcq_excel, sheet_name=name, index_col=0)["mos"]
    mos_df = mos_df.drop(golden.index, axis=0)
    return mos_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", default='labels', help="Directory of original pugcq subject labels.")
    parser.add_argument("-o", "--output_dir", default='outputs', help="Directory of output mos.")
    args = parser.parse_args()

    # get input excel list
    pugcq_excel_list = utils.get_file_list(args.input_dir, "pugcq")
    golden_excel_list = utils.get_file_list(args.input_dir, "golden")
    assert len(pugcq_excel_list) == len(golden_excel_list)
    pugcq_excel_list.sort()
    golden_excel_list.sort()

    # get mos with filter rule
    mos_combine_df = pd.DataFrame()
    for i in range(len(pugcq_excel_list)):
        print(pugcq_excel_list[i], golden_excel_list[i])
        mos_df = handle(pugcq_excel_list[i], golden_excel_list[i], args.output_dir)
        mos_combine_df = mos_df if i == 0 else mos_combine_df.append(mos_df)
        print()

    # merge with basic info
    basic_info_path = os.path.join(args.input_dir, "basic_info.xls")
    basic_info = pd.read_excel(basic_info_path, index_col=0)
    mos_combine_df = pd.merge(basic_info, mos_combine_df, left_index=True, right_index=True)

    # output combine mos
    output_mos_path = os.path.join(args.output_dir, "pugcq_mos.xls")
    mos_combine_writer = pd.ExcelWriter(output_mos_path)
    mos_combine_df.to_excel(mos_combine_writer, float_format="%0.2f")
    mos_combine_writer.save()

    print("done")
