#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создаем улучшенный мапинг стран с использованием стандартных ISO кодов
"""

import pandas as pd
import numpy as np

def create_comprehensive_country_mapping():
    """Создаем полный мапинг стран"""
    
    print("=== СОЗДАНИЕ УЛУЧШЕННОГО МАПИНГА СТРАН ===")
    
    # Загружаем данные
    trade_data = pd.read_csv('/workspace/data/final_trade_data.csv')
    countries_original = pd.read_csv('/workspace/user_input_files/countries.csv')
    
    # Получаем все уникальные коды стран из торговых данных
    unique_partner_codes = sorted(trade_data['partnerCode'].unique())
    print(f"Всего уникальных кодов стран в торговых данных: {len(unique_partner_codes)}")
    
    # Стандартные ISO 3166-1 numeric коды основных стран
    iso_country_mapping = {
        # Европа
        276: {"name": "Германия", "region": "Европа"},
        752: {"name": "Швеция", "region": "Европа"},
        208: {"name": "Дания", "region": "Европа"},
        578: {"name": "Норвегия", "region": "Европа"},
        528: {"name": "Нидерланды", "region": "Европа"},
        250: {"name": "Франция", "region": "Европа"},
        826: {"name": "Великобритания", "region": "Европа"},
        380: {"name": "Италия", "region": "Европа"},
        724: {"name": "Испания", "region": "Европа"},
        616: {"name": "Польша", "region": "Европа"},
        56: {"name": "Бельгия", "region": "Европа"},
        203: {"name": "Чехия", "region": "Европа"},
        348: {"name": "Венгрия", "region": "Европа"},
        703: {"name": "Словакия", "region": "Европа"},
        705: {"name": "Словения", "region": "Европа"},
        233: {"name": "Эстония", "region": "Европа"},
        428: {"name": "Латвия", "region": "Европа"},
        440: {"name": "Литва", "region": "Европа"},
        372: {"name": "Ирландия", "region": "Европа"},
        40: {"name": "Австрия", "region": "Европа"},
        756: {"name": "Швейцария", "region": "Европа"},
        300: {"name": "Греция", "region": "Европа"},
        620: {"name": "Португалия", "region": "Европа"},
        100: {"name": "Болгария", "region": "Европа"},
        642: {"name": "Румыния", "region": "Европа"},
        191: {"name": "Хорватия", "region": "Европа"},
        643: {"name": "Россия", "region": "Европа"},
        804: {"name": "Украина", "region": "Европа"},
        112: {"name": "Беларусь", "region": "Европа"},
        498: {"name": "Молдова", "region": "Европа"},
        
        # Азия
        156: {"name": "Китай", "region": "Азия"},
        392: {"name": "Япония", "region": "Азия"},
        410: {"name": "Южная Корея", "region": "Азия"},
        356: {"name": "Индия", "region": "Азия"},
        702: {"name": "Сингапур", "region": "Азия"},
        764: {"name": "Таиланд", "region": "Азия"},
        458: {"name": "Малайзия", "region": "Азия"},
        704: {"name": "Вьетнам", "region": "Азия"},
        360: {"name": "Индонезия", "region": "Азия"},
        608: {"name": "Филиппины", "region": "Азия"},
        784: {"name": "ОАЭ", "region": "Азия"},
        682: {"name": "Саудовская Аравия", "region": "Азия"},
        792: {"name": "Турция", "region": "Азия"},
        368: {"name": "Ирак", "region": "Азия"},
        364: {"name": "Иран", "region": "Азия"},
        398: {"name": "Казахстан", "region": "Азия"},
        860: {"name": "Узбекистан", "region": "Азия"},
        
        # Америка
        840: {"name": "США", "region": "Америка"},
        124: {"name": "Канада", "region": "Америка"},
        484: {"name": "Мексика", "region": "Америка"},
        76: {"name": "Бразилия", "region": "Америка"},
        32: {"name": "Аргентина", "region": "Америка"},
        152: {"name": "Чили", "region": "Америка"},
        170: {"name": "Колумбия", "region": "Америка"},
        604: {"name": "Перу", "region": "Америка"},
        858: {"name": "Уругвай", "region": "Америка"},
        
        # Африка
        710: {"name": "ЮАР", "region": "Африка"},
        818: {"name": "Египет", "region": "Африка"},
        12: {"name": "Алжир", "region": "Африка"},
        504: {"name": "Марокко", "region": "Африка"},
        566: {"name": "Нигерия", "region": "Африка"},
        404: {"name": "Кения", "region": "Африка"},
        
        # Океания
        36: {"name": "Австралия", "region": "Австралия и Океания"},
        554: {"name": "Новая Зеландия", "region": "Австралия и Океания"},
        
        # Специальные коды
        842: {"name": "США (континентальные)", "region": "Америка"},  # США континентальные
        579: {"name": "Норвегия (континентальная)", "region": "Европа"},  # Норвегия континентальная
        251: {"name": "Франция (континентальная)", "region": "Европа"},  # Франция континентальная
    }
    
    # Создаем итоговый мапинг
    final_mapping = []
    
    for code in unique_partner_codes:
        if code in iso_country_mapping:
            country_info = iso_country_mapping[code]
            final_mapping.append({
                'partnerCode': code,
                'country_name': country_info['name'],
                'world_part': country_info['region']
            })
        else:
            # Для неизвестных стран используем стандартное название
            final_mapping.append({
                'partnerCode': code,
                'country_name': f"Страна {code}",
                'world_part': "Прочие регионы"
            })
    
    # Создаем DataFrame
    mapping_df = pd.DataFrame(final_mapping)
    
    # Сохраняем
    mapping_df.to_csv('/workspace/data/country_mapping_enhanced.csv', index=False)
    
    print(f"Создан улучшенный мапинг: {len(mapping_df)} стран")
    print("\nРаспределение по регионам:")
    region_counts = mapping_df['world_part'].value_counts()
    print(region_counts)
    
    print(f"\nСтран с реальными названиями: {len(mapping_df[~mapping_df['country_name'].str.contains('Страна')])}")
    print(f"Стран остались как 'Страна XXX': {len(mapping_df[mapping_df['country_name'].str.contains('Страна')])}")
    
    return mapping_df

def create_final_dataset_with_fixed_countries():
    """Создаем финальный датасет с исправленными странами"""
    
    print("\n=== СОЗДАНИЕ ФИНАЛЬНОГО ДАТАСЕТА ===")
    
    # Загружаем данные
    trade_data = pd.read_csv('/workspace/data/final_trade_data.csv')
    enhanced_mapping = pd.read_csv('/workspace/data/country_mapping_enhanced.csv')
    
    # Удаляем старые колонки стран
    trade_data = trade_data.drop(['country_name', 'world_part'], axis=1, errors='ignore')
    
    # Присоединяем новый мапинг
    trade_final = trade_data.merge(
        enhanced_mapping,
        on='partnerCode',
        how='left'
    )
    
    # Заполняем пропуски
    trade_final['country_name'] = trade_final['country_name'].fillna('Неизвестная страна')
    trade_final['world_part'] = trade_final['world_part'].fillna('Прочие регионы')
    
    # Сохраняем
    trade_final.to_csv('/workspace/data/trade_data_fixed.csv', index=False)
    
    print(f"Финальный датасет: {len(trade_final)} записей")
    print(f"Уникальных стран: {trade_final['country_name'].nunique()}")
    
    # Статистика по топ партнерам (2019-2023)
    recent_data = trade_final[trade_final['period'] >= 2019]
    top_partners = recent_data.groupby('country_name')['trade_value_mln_usd'].sum().sort_values(ascending=False)
    
    print("\nТоп-10 партнеров (2019-2023) после исправлений:")
    for i, (country, value) in enumerate(top_partners.head(10).items(), 1):
        print(f"{i:2d}. {country}: ${value:.0f} млн USD")
    
    return trade_final

if __name__ == "__main__":
    mapping = create_comprehensive_country_mapping()
    final_data = create_final_dataset_with_fixed_countries()
