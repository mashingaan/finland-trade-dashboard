#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализируем проблемы в данных для доработки дашборда
"""

import pandas as pd
import numpy as np

def analyze_current_issues():
    """Анализируем текущие проблемы в данных"""
    
    print("=== АНАЛИЗ ПРОБЛЕМ В ДАННЫХ ===")
    
    # Загружаем данные
    trade_data = pd.read_csv('/workspace/data/final_trade_data.csv')
    country_mapping = pd.read_csv('/workspace/data/country_mapping.csv')
    countries_original = pd.read_csv('/workspace/user_input_files/countries.csv')
    
    print(f"Trade data shape: {trade_data.shape}")
    print(f"Country mapping shape: {country_mapping.shape}")
    print(f"Original countries shape: {countries_original.shape}")
    
    # Проблема 1: "Страна XXX" в country_mapping
    print("\n=== ПРОБЛЕМА 1: 'Страна XXX' в названиях ===")
    fake_countries = country_mapping[country_mapping['country_name'].str.contains('Страна', na=False)]
    print(f"Количество 'Страна XXX': {len(fake_countries)}")
    print("Примеры:")
    print(fake_countries.head(10))
    
    # Проверяем, можем ли мы найти их в оригинальных данных
    fake_codes = set(fake_countries['partnerCode'].values)
    print(f"\nКоды стран без названий: {sorted(list(fake_codes))[:10]}")
    
    # Ищем в оригинальных данных
    for code in sorted(list(fake_codes))[:5]:
        original_match = countries_original[countries_original['id'] == code]
        if not original_match.empty:
            print(f"Код {code}: найден как '{original_match.iloc[0]['text']}'")
        else:
            print(f"Код {code}: не найден в оригинальных данных")
    
    # Проблема 2: world_part issues
    print("\n=== ПРОБЛЕМА 2: world_part значения ===")
    world_parts = country_mapping['world_part'].value_counts(dropna=False)
    print("Распределение по регионам:")
    print(world_parts)
    
    # Ищем NULL/пустые значения
    null_world_parts = country_mapping[country_mapping['world_part'].isnull() | 
                                       (country_mapping['world_part'] == '') |
                                       (country_mapping['world_part'] == 'Неизвестно')]
    print(f"\nСтраны с проблемными world_part: {len(null_world_parts)}")
    if len(null_world_parts) > 0:
        print("Примеры:")
        print(null_world_parts.head())
    
    # Проблема 3: Топ-10 партнеров
    print("\n=== ПРОБЛЕМА 3: ТОП-10 ПАРТНЕРОВ (2019-2023) ===")
    
    # Фильтруем данные за последние 5 лет
    recent_data = trade_data[trade_data['period'] >= 2019].copy()
    
    # Группируем по странам
    partner_stats = recent_data.groupby(['partnerCode', 'country_name']).agg({
        'trade_value_mln_usd': 'sum'
    }).reset_index()
    
    # Топ-10 по объему
    top_partners = partner_stats.nlargest(10, 'trade_value_mln_usd')
    print("Топ-10 партнеров (2019-2023):")
    for _, row in top_partners.iterrows():
        print(f"  {row['country_name']}: ${row['trade_value_mln_usd']:.0f} млн USD")
    
    # Проблема 4: Товарные группы и их названия
    print("\n=== ПРОБЛЕМА 4: ТОВАРНЫЕ ГРУППЫ ===")
    commodities = trade_data['commodity_name'].value_counts()
    print("Топ-10 товарных групп:")
    for commodity, count in commodities.head(10).items():
        print(f"  {commodity[:50]}{'...' if len(commodity) > 50 else ''}: {count} записей")
    
    return trade_data, country_mapping, countries_original

def fix_country_mapping():
    """Исправляем мапинг стран"""
    
    print("\n=== ИСПРАВЛЕНИЕ МАПИНГА СТРАН ===")
    
    # Загружаем данные
    country_mapping = pd.read_csv('/workspace/data/country_mapping.csv')
    countries_original = pd.read_csv('/workspace/user_input_files/countries.csv')
    
    # Создаем улучшенный мапинг
    fixed_mapping = country_mapping.copy()
    
    # Исправляем "Страна XXX"
    for idx, row in country_mapping.iterrows():
        if 'Страна' in str(row['country_name']):
            code = row['partnerCode']
            
            # Ищем в оригинальных данных
            original_match = countries_original[countries_original['id'] == code]
            if not original_match.empty:
                original_name = original_match.iloc[0]['text']
                original_world_part = original_match.iloc[0]['world_part']
                
                fixed_mapping.at[idx, 'country_name'] = original_name
                if pd.isna(row['world_part']) or row['world_part'] == 'Неизвестно':
                    fixed_mapping.at[idx, 'world_part'] = original_world_part
                
                print(f"Исправлено: {code} -> {original_name} ({original_world_part})")
    
    # Исправляем world_part
    fixed_mapping['world_part'] = fixed_mapping['world_part'].fillna('Прочие регионы')
    fixed_mapping.loc[fixed_mapping['world_part'] == '', 'world_part'] = 'Прочие регионы'
    fixed_mapping.loc[fixed_mapping['world_part'] == 'Неизвестно', 'world_part'] = 'Прочие регионы'
    fixed_mapping.loc[fixed_mapping['world_part'] == 'world_part', 'world_part'] = 'Прочие регионы'
    
    # Сохраняем исправленный мапинг
    fixed_mapping.to_csv('/workspace/data/country_mapping_fixed.csv', index=False)
    
    print(f"\nИсправленный мапинг сохранен: {len(fixed_mapping)} стран")
    print("Распределение по регионам:")
    print(fixed_mapping['world_part'].value_counts())
    
    return fixed_mapping

if __name__ == "__main__":
    trade_data, country_mapping, countries_original = analyze_current_issues()
    fixed_mapping = fix_country_mapping()
