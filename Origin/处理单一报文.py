import originpro as op
import pandas as pd

# 指定工作簿名称
book_name = "Book1204PM"  # 根据需求更改为你的工作簿名称

# 获取工作簿
workbook = op.find_book(name=book_name)

if workbook:
    print(f"Workbook found: {workbook.name}")

    # 假设sheet的名字存储在 comments 中
    sheet_names = workbook.comments.split('\n')  # 假设sheet名字按换行符分隔
    print(f"Sheet names found: {sheet_names}")

    result_book = op.find_book(name='PREP1204PM')
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

        filtered_df = df[df['ID (hex)'].isin(['048D',])]
        # print(filtered_df.head())
        # print(filtered_df.tail())
        # print(filtered_df.iloc[0,4])
        # print(len(filtered_df))
        # print(filtered_df.iloc[991,4])

        print(filtered_df['ID (hex)'].head())
        print(filtered_df['ID (hex)'].tail())


        # 处理E列为48D的行并计算 y
        df_48D = df[df['ID (hex)'] == '048D'].copy()
        df_48D['y'] = df_48D['Byte2'] + df_48D['Byte3'] * 256
        df_48D['z'] = df_48D['Byte4'] + df_48D['Byte5'] * 256
        print('-' * 20)
        print(df_48D.shape)
  
        # 提取反馈与指令速度
        df_result = pd.DataFrame({'反馈速度': df_48D['y'].values, '指令速度': df_48D['z'].values})
        
        # 在结果工作簿中创建一个新的sheet，与原来的sheet同名
        result_worksheet = result_book.add_sheet(sheet_name[:-5])

        # 将结果数据写入到新的sheet中
        result_worksheet.from_df(df_result)

    print("Processing completed! New workbook with processed data created.")
else:
    print("Workbook not found")
