#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исследования структуры данных по внешней торговле Финляндии
"""

import pandas as pd
import sqlite3
import numpy as np

def explore_csv_files():
    """Исследование CSV файлов"""
    
    # Commodities
    print("=== COMMODITIES ===")
    commodities = pd.read_csv('/workspace/user_input_files/commodities.csv')
    print(f"Shape: {commodities.shape}")
    print(f"Columns: {commodities.columns.tolist()}")
    print("Sample:")
    print(commodities.head(10))
    print("\nUnique sectors:")
    print(commodities['sector'].unique())
    print("\n")
    
    # Countries  
    print("=== COUNTRIES ===")
    countries = pd.read_csv('/workspace/user_input_files/countries.csv')
    print(f"Shape: {countries.shape}")
    print(f"Columns: {countries.columns.tolist()}")
    print("Sample:")
    print(countries.head(10))
    print("\nUnique world parts:")
    print(countries['world_part'].unique())
    print("\n")
    
    # Trade
    print("=== TRADE ===")
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    print(f"Shape: {trade.shape}")
    print(f"Columns: {trade.columns.tolist()}")
    print("Sample:")
    print(trade.head(10))
    print(f"\nPeriod range: {trade['period'].min()} - {trade['period'].max()}")
    print(f"Unique flow codes: {trade['flowCode'].unique()}")
    print(f"Unique reporter codes: {trade['reporterCode'].unique()}")
    print(f"Partner codes count: {trade['partnerCode'].nunique()}")
    print(f"Commodity codes count: {trade['cmdCode'].nunique()}")
    print("\n")

def explore_database():
    """Исследование базы данных"""
    
    print("=== FINLAND.DB ===")
    try:
        conn = sqlite3.connect('/workspace/user_input_files/Finland.db')
        
        # Получаем список таблиц
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[table[0] for table in tables]}")
        
        # Исследуем каждую таблицу
        for table in tables:
            table_name = table[0]
            print(f"\n--- Table: {table_name} ---")
            
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10", conn)
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            print("Sample:")
            print(df.head())
            
        conn.close()
        
    except Exception as e:
        print(f"Error exploring database: {e}")

def check_data_relationships():
    """Проверяем связи между данными"""
    
    print("=== DATA RELATIONSHIPS ===")
    
    # Загружаем данные
    commodities = pd.read_csv('/workspace/user_input_files/commodities.csv')
    countries = pd.read_csv('/workspace/user_input_files/countries.csv')
    trade = pd.read_csv('/workspace/user_input_files/trade.csv')
    
    # Проверяем связи
    print(f"Trade cmdCode range: {trade['cmdCode'].min()} - {trade['cmdCode'].max()}")
    print(f"Commodities id range: {commodities['id'].min()} - {commodities['id'].max()}")
    
    print(f"Trade partnerCode unique count: {trade['partnerCode'].nunique()}")
    print(f"Countries id unique count: {countries['id'].nunique()}")
    
    # Проверяем пересечения
    trade_cmd_codes = set(trade['cmdCode'].unique())
    commodities_ids = set(commodities['id'].unique())
    print(f"cmdCode intersection: {len(trade_cmd_codes.intersection(commodities_ids))}")
    
    trade_partner_codes = set(trade['partnerCode'].unique())
    countries_ids = set(countries['id'].unique())
    print(f"partnerCode intersection: {len(trade_partner_codes.intersection(countries_ids))}")
    
    # Проверяем на пропуски
    print(f"\nTrade missing values:")
    print(trade.isnull().sum())
    
    print(f"\nData types in trade:")
    print(trade.dtypes)

if __name__ == "__main__":
    explore_csv_files()
    explore_database()
    check_data_relationships()
