# -*- coding: utf-8 -*-
"""
数据清洗模块
使用Pandas对爬取的景点数据进行清洗处理
"""

import pandas as pd
import json
import os
from config import DATA_DIR


def load_data(filename='attractions.json'):
    """加载JSON数据"""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def clean_data(df):
    """数据清洗"""
    print(f"原始数据: {len(df)} 条")
    
    # 1. 删除重复值（根据名称和城市去重）
    df = df.drop_duplicates(subset=['name', 'city'], keep='first')
    print(f"去重后: {len(df)} 条")
    
    # 2. 处理空值
    df['name'] = df['name'].fillna('')
    df['address'] = df['address'].fillna('')
    df['description'] = df['description'].fillna('')
    df['image_url'] = df['image_url'].fillna('')
    df['level'] = df['level'].fillna('')
    
    # 删除名称为空的记录
    df = df[df['name'].str.strip() != '']
    print(f"删除空名称后: {len(df)} 条")
    
    # 3. 数值类型转换和处理
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
    df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0).astype(int)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0)
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0)
    
    # 4. 评分范围处理（0-5分）
    df.loc[df['score'] > 5, 'score'] = 5
    df.loc[df['score'] < 0, 'score'] = 0
    
    # 5. 价格处理（负数设为0）
    df.loc[df['price'] < 0, 'price'] = 0
    
    # 6. 字符串清洗（去除首尾空格）
    df['name'] = df['name'].str.strip()
    df['address'] = df['address'].str.strip()
    df['city'] = df['city'].str.strip()
    df['province'] = df['province'].str.strip()
    
    print(f"清洗完成: {len(df)} 条")
    return df


def analyze_data(df):
    """数据分析概览"""
    print("\n" + "=" * 50)
    print("数据分析概览")
    print("=" * 50)
    
    print(f"\n总景点数: {len(df)}")
    print(f"覆盖省份: {df['province'].nunique()} 个")
    print(f"覆盖城市: {df['city'].nunique()} 个")
    
    print(f"\n评分统计:")
    print(f"  平均评分: {df['score'].mean():.2f}")
    print(f"  最高评分: {df['score'].max():.1f}")
    print(f"  最低评分: {df[df['score'] > 0]['score'].min():.1f}")
    
    print(f"\n评论数统计:")
    print(f"  总评论数: {df['comment_count'].sum():,}")
    print(f"  平均评论: {df['comment_count'].mean():.0f}")
    
    print(f"\n各省份景点数:")
    print(df['province'].value_counts().to_string())
    
    print(f"\n评论数TOP10景点:")
    top10 = df.nlargest(10, 'comment_count')[['name', 'city', 'score', 'comment_count']]
    print(top10.to_string(index=False))


def save_cleaned_data(df, filename='attractions_cleaned.csv'):
    """保存清洗后的数据"""
    filepath = os.path.join(DATA_DIR, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"\n清洗后数据已保存到: {filepath}")
    return filepath


def main():
    # 加载数据
    df = load_data()
    
    # 清洗数据
    df = clean_data(df)
    
    # 数据分析
    analyze_data(df)
    
    # 保存清洗后的数据
    save_cleaned_data(df)
    
    return df


if __name__ == '__main__':
    main()
