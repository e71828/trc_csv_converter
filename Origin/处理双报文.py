import originpro as op
import pandas as pd

# 指定工作簿名称
book_name = "AAA"  # 根据需求更改为你的工作簿名称

# 获取工作簿
workbook = op.find_book(name=book_name)

if workbook:
    print(f"Workbook found: {workbook.name}")

    # 假设sheet的名字存储在 comments 中
    sheet_names = workbook.comments.split('\n')  # 假设sheet名字按换行符分隔
    print(f"Sheet names found: {sheet_names}")

    result_book = op.find_book(name='PREPrp')
    sheet_names[-1] += '\r'

    # 循环处理每个工作表
    for sheet_name in sheet_names:
        # print(sheet_name)
        sheet = workbook[sheet_name[:-5]]  # 获取原始工作簿中的sheet

        # 将sheet转换为pandas DataFrame
        df = sheet.to_df()  # 假设 originpro 支持将 sheet 转换为 DataFrame
        # print(df.columns)  # 打印列名进行检查
        # print(df.head())
        # print(df.tail())

        df['ID (hex)'] = df['ID (hex)'].astype(str)

        filtered_df = df[df['ID (hex)'].isin(['048F', '038C'])]
        # print(filtered_df.head())
        # print(filtered_df.tail())
        # print(filtered_df.iloc[0,4])
        # print(len(filtered_df))
        # print(filtered_df.iloc[991,4])

        overl = []
        for i in range(1, len(filtered_df) - 1):
            if filtered_df.iloc[i, 4] == filtered_df.iloc[i - 1, 4]:
                overl.append(i - 1)

        print(overl)
        filtered_df.drop(filtered_df.index[overl], inplace=True)
        filtered_df.reset_index(drop=True, inplace=True)

        if filtered_df.iloc[0, 4] == '048F':
            filtered_df.drop(0, inplace=True)
            print('drop once')

        filtered_df.reset_index(drop=True, inplace=True)
        if filtered_df.iloc[len(filtered_df) - 1, 4] != '048F':
            filtered_df.drop(len(filtered_df) - 1, inplace=True)
            print('drop once')

        filtered_df.reset_index(drop=True, inplace=True)
        print(filtered_df['ID (hex)'].head())
        print(filtered_df['ID (hex)'].tail())

        df = filtered_df.copy()
        df_038C  = df[df['ID (hex)'] == '038C'].copy()


        df_038C ['x'] = df_038C ['Byte4'] + df_038C ['Byte5'] * 256
        print('-' * 20)
        print(df_038C .shape)

        # 处理E列为18D的行并计算 y
        df_048F = df[df['ID (hex)'] == '048F'].copy()
        df_048F['y'] = df_048F['Byte2'] + df_048F['Byte3'] * 256
        print('-' * 20)
        print(df_048F.shape)
        
        # 获取两列数据长度的最小值
        min_length = min(len(df_038C ['x']), len(df_048F['y']))

        # 截取到相同长度，假设对应提取是按顺序匹配，可以使用DataFrame的索引
        df_result = pd.DataFrame({'倾角': df_038C ['x'].iloc[:min_length].values, '原力限器': df_048F['y'].iloc[:min_length].values})
        
        # 在结果工作簿中创建一个新的sheet，与原来的sheet同名
        result_worksheet = result_book.add_sheet(sheet_name[:-5])

        # 将结果数据写入到新的sheet中
        result_worksheet.from_df(df_result)

    print("Processing completed! New workbook with processed data created.")
else:
    print("Workbook not found")
