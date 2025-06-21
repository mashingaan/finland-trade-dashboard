#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Более детальное исследование связей в данных и подготовка данных для дашборда
"""

import pandas as pd
import numpy as np

def investigate_country_codes():
    """Исследуем коды стран и их связи"""
    
    print("=== ИССЛЕДОВАНИЕ КОДОВ СТРАН ===")
    
    # Загружаем данные
    countries = pd.read_csv('/workspace/user_input_files/countries.csv')
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    
    print(f"Unique partner codes in trade: {len(trade['partnerCode'].unique())}")
    print(f"Sample partner codes: {sorted(trade['partnerCode'].unique())[:20]}")
    
    print(f"\nUnique country ids: {len(countries['id'].unique())}")
    print(f"Sample country ids: {sorted(countries['id'].unique())[:20]}")
    
    # Проверяем, есть ли пересечения
    trade_partners = set(trade['partnerCode'].unique())
    country_ids = set(countries['id'].unique())
    intersection = trade_partners.intersection(country_ids)
    
    print(f"\nIntersection count: {len(intersection)}")
    
    if len(intersection) > 0:
        print(f"Sample intersecting codes: {sorted(list(intersection))[:10]}")
        
        # Показываем примеры пересекающихся стран
        sample_codes = sorted(list(intersection))[:5]
        for code in sample_codes:
            country_name = countries[countries['id'] == code]['text'].iloc[0]
            trade_count = len(trade[trade['partnerCode'] == code])
            print(f"Code {code}: {country_name} - {trade_count} trade records")
    
    # Проверяем, может быть коды стран находятся в reporterCodeIsoAlpha3?
    print(f"\nChecking ISO codes...")
    iso_codes = countries['reporterCodeIsoAlpha3'].unique()
    print(f"Sample ISO codes: {iso_codes[:10]}")
    
    return trade, countries

def investigate_commodity_codes():
    """Исследуем коды товаров"""
    
    print("\n=== ИССЛЕДОВАНИЕ КОДОВ ТОВАРОВ ===")
    
    commodities = pd.read_csv('/workspace/user_input_files/commodities.csv')
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    
    print(f"Commodity codes in trade: {sorted(trade['cmdCode'].unique())[:20]}")
    print(f"Commodity ids: {sorted(commodities['id'].unique())[:20]}")
    
    # Проверяем пересечения
    trade_cmd = set(trade['cmdCode'].unique())
    commodity_ids = set(commodities['id'].unique())
    intersection = trade_cmd.intersection(commodity_ids)
    
    print(f"Commodity intersection: {len(intersection)} out of {len(trade_cmd)} trade codes")
    
    # Показываем секторы
    print(f"\nSectors:")
    sectors = commodities['sector'].value_counts()
    print(sectors)
    
    return trade, commodities

def analyze_data_completeness():
    """Анализируем полноту данных"""
    
    print("\n=== АНАЛИЗ ПОЛНОТЫ ДАННЫХ ===")
    
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    
    print(f"Total trade records: {len(trade)}")
    print(f"Period range: {trade['period'].min()} - {trade['period'].max()}")
    print(f"Flow codes: {trade['flowCode'].unique()}")
    
    # Анализируем по годам
    yearly_stats = trade.groupby('period').agg({
        'primaryValue': ['count', 'sum'],
        'partnerCode': 'nunique',
        'cmdCode': 'nunique'
    }).round(2)
    
    print("\nГодовая статистика:")
    print(yearly_stats)
    
    # Проверяем на нули и отрицательные значения
    print(f"\nЗначения торговли:")
    print(f"Zero values: {(trade['primaryValue'] == 0).sum()}")
    print(f"Negative values: {(trade['primaryValue'] < 0).sum()}")
    print(f"Min value: {trade['primaryValue'].min()}")
    print(f"Max value: {trade['primaryValue'].max()}")
    
    return trade

def create_master_dataset():
    """Создаем основной объединенный датасет"""
    
    print("\n=== СОЗДАНИЕ ОСНОВНОГО ДАТАСЕТА ===")
    
    # Загружаем данные
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    countries = pd.read_csv('/workspace/user_input_files/countries.csv')
    commodities = pd.read_csv('/workspace/user_input_files/commodities.csv')
    
    # Проверяем связи снова
    trade_partners = set(trade['partnerCode'].unique())
    country_ids = set(countries['id'].unique())
    common_countries = trade_partners.intersection(country_ids)
    
    print(f"Countries that can be linked: {len(common_countries)}")
    
    # Объединяем данные
    # Товары
    trade_with_commodities = trade.merge(
        commodities, 
        left_on='cmdCode', 
        right_on='id', 
        how='left',
        suffixes=('', '_commodity')
    )
    
    print(f"After commodity merge: {len(trade_with_commodities)} records")
    print(f"Records with commodity info: {trade_with_commodities['text'].notna().sum()}")
    
    # Страны - только те, что есть в пересечении
    if len(common_countries) > 0:
        trade_full = trade_with_commodities.merge(
            countries[['id', 'text', 'reporterCodeIsoAlpha3', 'world_part']], 
            left_on='partnerCode', 
            right_on='id', 
            how='left',
            suffixes=('', '_country')
        )
        
        print(f"After country merge: {len(trade_full)} records")
        print(f"Records with country info: {trade_full['text_country'].notna().sum()}")
    else:
        # Если нет прямых связей, создаем датасет без стран
        trade_full = trade_with_commodities.copy()
        trade_full['text_country'] = 'Unknown Country'
        trade_full['world_part'] = 'Unknown'
        trade_full['reporterCodeIsoAlpha3'] = None
        
        print("No direct country links found. Using placeholder values.")
    
    # Переименовываем колонки для ясности
    trade_full = trade_full.rename(columns={
        'text': 'commodity_name',
        'sector': 'commodity_sector',
        'text_country': 'country_name',
        'primaryValue': 'trade_value_usd'
    })
    
    # Конвертируем в миллионы USD
    trade_full['trade_value_mln_usd'] = trade_full['trade_value_usd'] / 1_000_000
    
    # Добавляем человекочитаемые названия потоков
    trade_full['flow_name'] = trade_full['flowCode'].map({
        'X': 'Экспорт',
        'M': 'Импорт'
    })
    
    # Сохраняем
    trade_full.to_csv('/workspace/data/master_trade_data.csv', index=False)
    
    print(f"\nMaster dataset saved: {len(trade_full)} records")
    print("Columns:", trade_full.columns.tolist())
    
    # Базовая статистика
    print(f"\nBasic statistics:")
    print(f"Years: {trade_full['period'].min()} - {trade_full['period'].max()}")
    print(f"Total trade value: ${trade_full['trade_value_mln_usd'].sum():.1f} mln USD")
    print(f"Export records: {(trade_full['flowCode'] == 'X').sum()}")
    print(f"Import records: {(trade_full['flowCode'] == 'M').sum()}")
    
    return trade_full

if __name__ == "__main__":
    # Создаем папку для данных
    import os
    os.makedirs('/workspace/data', exist_ok=True)
    
    trade, countries = investigate_country_codes()
    trade, commodities = investigate_commodity_codes()
    trade = analyze_data_completeness()
    
    master_data = create_master_dataset()
    
    print("\n=== ИССЛЕДОВАНИЕ ЗАВЕРШЕНО ===")
    print("Master dataset создан: /workspace/data/master_trade_data.csv")
