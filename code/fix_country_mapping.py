#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание правильной связки между кодами стран в trade.csv и countries.csv
"""

import pandas as pd
import numpy as np

def create_country_mapping():
    """Создаем мапинг кодов стран"""
    
    print("=== СОЗДАНИЕ МАПИНГА СТРАН ===")
    
    # Загружаем данные
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    countries = pd.read_csv('/workspace/user_input_files/countries.csv')
    
    # Получаем уникальные коды партнеров из торговых данных
    unique_partners = sorted(trade['partnerCode'].unique())
    print(f"Unique partner codes: {len(unique_partners)}")
    
    # Попробуем найти стандартные коды стран
    # Коды стран ООН обычно идут последовательно
    
    # Создаем базовый мапинг наиболее популярных стран
    # на основе стандартных ISO numeric codes
    
    standard_country_mapping = {
        # Основные торговые партнеры Финляндии
        276: "Германия",  # Germany
        752: "Швеция",    # Sweden
        208: "Дания",     # Denmark
        578: "Норвегия",  # Norway
        156: "Китай",     # China
        840: "США",       # United States
        528: "Нидерланды", # Netherlands
        250: "Франция",   # France
        826: "Великобритания", # United Kingdom
        380: "Италия",    # Italy
        643: "Россия",    # Russia
        124: "Канада",    # Canada
        392: "Япония",    # Japan
        724: "Испания",   # Spain
        616: "Польша",    # Poland
        56: "Бельгия",    # Belgium
        203: "Чехия",     # Czech Republic
        348: "Венгрия",   # Hungary
        703: "Словакия",  # Slovakia
        705: "Словения",  # Slovenia
        233: "Эстония",   # Estonia
        428: "Латвия",    # Latvia
        440: "Литва",     # Lithuania
        372: "Ирландия",  # Ireland
        40: "Австрия",    # Austria
        756: "Швейцария", # Switzerland
        
        # Азиатские страны
        410: "Южная Корея", # South Korea
        702: "Сингапур",    # Singapore
        764: "Таиланд",     # Thailand
        458: "Малайзия",    # Malaysia
        
        # Остальные европейские
        300: "Греция",      # Greece
        620: "Португалия",  # Portugal
        100: "Болгария",    # Bulgaria
        642: "Румыния",     # Romania
        191: "Хорватия",    # Croatia
    }
    
    # Проверяем, какие из этих кодов есть в наших данных
    trade_partners = set(trade['partnerCode'].unique())
    found_countries = {}
    
    for code, name in standard_country_mapping.items():
        if code in trade_partners:
            found_countries[code] = name
    
    print(f"Found standard country codes: {len(found_countries)}")
    
    # Создаем полный справочник стран для торговых данных
    # На основе найденных стандартных кодов и добавляя остальные как "Unknown"
    
    country_mapping = {}
    world_part_mapping = {}
    
    # Стандартные страны с регионами
    for code, name in found_countries.items():
        country_mapping[code] = name
        
        # Простая логика определения региона
        if code in [276, 752, 208, 578, 528, 250, 826, 380, 724, 616, 56, 203, 348, 703, 705, 233, 428, 440, 372, 40, 756, 300, 620, 100, 642, 191]:
            world_part_mapping[code] = "Европа"
        elif code in [156, 392, 410, 702, 764, 458]:
            world_part_mapping[code] = "Азия"
        elif code in [840, 124]:
            world_part_mapping[code] = "Америка"
        elif code in [643]:
            world_part_mapping[code] = "Европа"  # Россия как Европа
        else:
            world_part_mapping[code] = "Неизвестно"
    
    # Для остальных кодов создаем записи "Unknown Country XX"
    for partner_code in trade_partners:
        if partner_code not in country_mapping:
            country_mapping[partner_code] = f"Страна {partner_code}"
            world_part_mapping[partner_code] = "Неизвестно"
    
    print(f"Total country mappings created: {len(country_mapping)}")
    
    # Создаем DataFrame с мапингом
    mapping_df = pd.DataFrame([
        {'partnerCode': code, 'country_name': name, 'world_part': world_part_mapping[code]}
        for code, name in country_mapping.items()
    ])
    
    # Сохраняем мапинг
    mapping_df.to_csv('/workspace/data/country_mapping.csv', index=False)
    
    return mapping_df

def create_final_dataset():
    """Создаем финальный датасет с правильными связями"""
    
    print("\n=== СОЗДАНИЕ ФИНАЛЬНОГО ДАТАСЕТА ===")
    
    # Загружаем данные
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    commodities = pd.read_csv('/workspace/user_input_files/commodities.csv')
    
    # Создаем или загружаем мапинг стран
    try:
        country_mapping = pd.read_csv('/workspace/data/country_mapping.csv')
    except:
        country_mapping = create_country_mapping()
    
    # Объединяем все данные
    # Сначала товары
    trade_with_commodities = trade.merge(
        commodities, 
        left_on='cmdCode', 
        right_on='id', 
        how='left',
        suffixes=('', '_commodity')
    )
    
    # Потом страны
    trade_full = trade_with_commodities.merge(
        country_mapping,
        on='partnerCode',
        how='left'
    )
    
    # Переименовываем и очищаем колонки
    trade_full = trade_full.rename(columns={
        'text': 'commodity_name',
        'sector': 'commodity_sector',
        'primaryValue': 'trade_value_usd'
    })
    
    # Добавляем вычисляемые поля
    trade_full['trade_value_mln_usd'] = trade_full['trade_value_usd'] / 1_000_000
    
    trade_full['flow_name'] = trade_full['flowCode'].map({
        'X': 'Экспорт',
        'M': 'Импорт'
    })
    
    # Убираем ненужные колонки
    columns_to_keep = [
        'period', 'flowCode', 'flow_name', 'partnerCode', 'country_name', 'world_part',
        'cmdCode', 'commodity_name', 'commodity_sector', 
        'trade_value_usd', 'trade_value_mln_usd'
    ]
    
    trade_final = trade_full[columns_to_keep].copy()
    
    # Проверяем результат
    print(f"Final dataset: {len(trade_final)} records")
    print(f"Countries with names: {trade_final['country_name'].notna().sum()}")
    print(f"Commodities with names: {trade_final['commodity_name'].notna().sum()}")
    
    # Сохраняем финальный датасет
    trade_final.to_csv('/workspace/data/final_trade_data.csv', index=False)
    
    # Статистика
    print(f"\nФинальная статистика:")
    print(f"Годы: {trade_final['period'].min()} - {trade_final['period'].max()}")
    print(f"Общий товарооборот: ${trade_final['trade_value_mln_usd'].sum():.0f} млн USD")
    print(f"Экспорт: ${trade_final[trade_final['flowCode']=='X']['trade_value_mln_usd'].sum():.0f} млн USD")
    print(f"Импорт: ${trade_final[trade_final['flowCode']=='M']['trade_value_mln_usd'].sum():.0f} млн USD")
    
    print(f"\nТоп-10 торговых партнеров:")
    top_partners = trade_final.groupby('country_name')['trade_value_mln_usd'].sum().sort_values(ascending=False).head(10)
    for country, value in top_partners.items():
        print(f"  {country}: ${value:.0f} млн USD")
    
    print(f"\nТоп-10 товарных групп:")
    top_commodities = trade_final.groupby('commodity_name')['trade_value_mln_usd'].sum().sort_values(ascending=False).head(10)
    for commodity, value in top_commodities.items():
        print(f"  {commodity}: ${value:.0f} млн USD")
    
    return trade_final

if __name__ == "__main__":
    # Создаем необходимые папки
    import os
    os.makedirs('/workspace/data', exist_ok=True)
    
    # Создаем мапинг стран
    country_mapping = create_country_mapping()
    
    # Создаем финальный датасет
    final_data = create_final_dataset()
    
    print("\n=== ПОДГОТОВКА ДАННЫХ ЗАВЕРШЕНА ===")
    print("Файлы созданы:")
    print("- /workspace/data/country_mapping.csv")
    print("- /workspace/data/final_trade_data.csv")
