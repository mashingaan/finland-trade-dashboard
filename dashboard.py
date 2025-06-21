#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash_bootstrap_components import themes
import dash_bootstrap_components as dbc

# Загрузка данных
def load_data():
    # Загружаем основные данные
    trade_df = pd.read_csv('trade.csv')
    countries_df = pd.read_csv('countries.csv')
    commodities_df = pd.read_csv('commodities.csv')
    
    # Переименовываем колонки для удобства
    trade_df = trade_df.rename(columns={
        'period': 'year',
        'reporterCode': 'reporterCode',
        'flowCode': 'flow',
        'partnerCode': 'partnerCode',
        'cmdCode': 'commodityCode',
        'primaryValue': 'value'
    })
    
    # Создаем маппинг стран
    country_mapping = dict(zip(countries_df['id'], countries_df['text']))
    
    # Обрабатываем данные
    trade_df['partnerName'] = trade_df['partnerCode'].map(country_mapping)
    trade_df['partnerName'] = trade_df['partnerName'].fillna('Прочие регионы')
    
    # Убираем категорию "Неизвестно"
    trade_df = trade_df[trade_df['partnerName'] != 'Неизвестно']
    
    # Заменяем коды стран на названия
    trade_df.loc[trade_df['partnerCode'] == 842, 'partnerName'] = 'США'
    trade_df.loc[trade_df['partnerCode'] == 579, 'partnerName'] = 'Норвегия'
    
    return trade_df, countries_df, commodities_df

# Функция форматирования чисел
def format_number(value):
    if pd.isna(value) or value == 0:
        return "0"
    
    if abs(value) >= 1e9:
        return f"{value/1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return f"{value:.0f}"

# Функция форматирования для tooltip
def format_tooltip(value):
    if pd.isna(value) or value == 0:
        return "0 млн USD"
    
    if abs(value) >= 1e9:
        return f"{value/1e9:.1f}B млн USD"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.1f}M млн USD"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.1f}K млн USD"
    else:
        return f"{value:.0f} млн USD"

# Загружаем данные
trade_df, countries_df, commodities_df = load_data()

# Создаем Dash приложение
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE, "/assets/custom.css"])
server = app.server

# Макет приложения
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    # Заголовок
    dbc.Row([
        dbc.Col([
            html.H1("🇫🇮 Дашборд внешней торговли Финляндии", 
                   className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    # KPI карточки
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Общий товарооборот", className="card-title"),
                    html.H2(id="total-trade", className="text-primary")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Торговое сальдо 2023", className="card-title"),
                    html.H2(id="trade-balance", className="text-success")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Топ партнер", className="card-title"),
                    html.H2(id="top-partner", className="text-info")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Период", className="card-title"),
                    html.H2("2000-2023", className="text-warning")
                ])
            ])
        ], width=3)
    ], className="mb-4"),
    
    # Вкладки
    dbc.Tabs([
        # Вкладка 1: Динамика по годам
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="yearly-trend")
                ])
            ])
        ], label="Динамика по годам"),
        
        # Вкладка 2: ТОП-10 товарных групп
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(
                        id="commodity-type",
                        options=[
                            {"label": "Экспорт", "value": "E"},
                            {"label": "Импорт", "value": "I"}
                        ],
                        value="E",
                        inline=True,
                        className="mb-3"
                    ),
                    dcc.Graph(id="top-commodities")
                ])
            ])
        ], label="ТОП-10 товарных групп"),
        
        # Вкладка 3: Структура по секторам
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="sector-structure")
                ])
            ])
        ], label="Структура по секторам"),
        
        # Вкладка 4: География торговли
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="geography-map")
                ])
            ])
        ], label="География торговли"),
        
        # Вкладка 5: ТОП-10 стран-партнеров
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="top-partners")
                ])
            ])
        ], label="ТОП-10 стран-партнеров"),
        
        # Вкладка 6: Российская Федерация
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="russia-analysis")
                ])
            ])
        ], label="Российская Федерация"),
        
        # Вкладка 7: Изменения структуры
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="structure-changes")
                ])
            ])
        ], label="Изменения структуры")
    ])
], fluid=True)

# Callback для KPI карточек
@app.callback(
    [Output("total-trade", "children"),
     Output("trade-balance", "children"),
     Output("top-partner", "children")],
    [Input("url", "pathname")]
)
def update_kpi(pathname):
    # Общий товарооборот
    total_trade = trade_df['value'].sum()
    
    # Торговое сальдо 2023
    recent_data = trade_df[trade_df['year'] == 2023]
    if not recent_data.empty:
        exports = recent_data[recent_data['flow'] == 'E']['value'].sum()
        imports = recent_data[recent_data['flow'] == 'I']['value'].sum()
        balance = exports - imports
        balance_text = f"{format_number(balance)}"
        if balance > 0:
            balance_text = f"+{balance_text} 📈"
        else:
            balance_text = f"{balance_text} 📉"
    else:
        balance_text = "N/A"
    
    # Топ партнер
    partner_totals = trade_df.groupby('partnerName')['value'].sum().sort_values(ascending=False)
    top_partner = partner_totals.index[0] if not partner_totals.empty else "N/A"
    
    return f"{format_number(total_trade)} млн USD", balance_text, top_partner

# Callback для динамики по годам
@app.callback(
    Output("yearly-trend", "figure"),
    [Input("url", "pathname")]
)
def update_yearly_trend(pathname):
    yearly_data = trade_df.groupby(['year', 'flow'])['value'].sum().reset_index()
    
    # Переименовываем потоки для лучшего отображения
    flow_mapping = {'E': 'Экспорт', 'I': 'Импорт'}
    yearly_data['flow'] = yearly_data['flow'].map(flow_mapping)
    
    fig = px.line(yearly_data, x='year', y='value', color='flow',
                  title="Динамика экспорта и импорта по годам",
                  labels={'value': 'Объем торговли (млн USD)', 'year': 'Год', 'flow': 'Тип потока'})
    
    fig.update_traces(hovertemplate='%{y:,.0f} млн USD<extra></extra>')
    fig.update_layout(template="plotly_white")
    
    return fig

# Callback для ТОП-10 товарных групп
@app.callback(
    Output("top-commodities", "figure"),
    [Input("commodity-type", "value")]
)
def update_top_commodities(commodity_type):
    commodity_data = trade_df[trade_df['flow'] == commodity_type].groupby('commodityCode')['value'].sum().reset_index()
    commodity_data = commodity_data.merge(commodities_df, left_on='commodityCode', right_on='id', how='left')
    commodity_data = commodity_data.nlargest(10, 'value')
    
    # Обрезаем названия до 30 символов
    commodity_data['short_name'] = commodity_data['text'].apply(
        lambda x: x[:30] + '...' if len(str(x)) > 30 else str(x)
    )
    
    flow_name = "Экспорт" if commodity_type == "E" else "Импорт"
    
    fig = px.bar(commodity_data, x='value', y='short_name', orientation='h',
                 title=f"ТОП-10 товарных групп ({flow_name})",
                 labels={'value': 'Объем торговли (млн USD)', 'short_name': 'Товарная группа'})
    
    fig.update_traces(hovertemplate='%{y}<br>%{x:,.0f} млн USD<extra></extra>')
    fig.update_layout(template="plotly_white")
    
    return fig

# Callback для структуры по секторам
@app.callback(
    Output("sector-structure", "figure"),
    [Input("url", "pathname")]
)
def update_sector_structure(pathname):
    # Группируем по первым цифрам кода товара (сектора)
    trade_df['sector'] = trade_df['commodityCode'].astype(str).str[:2]
    sector_data = trade_df.groupby('sector')['value'].sum().reset_index()
    sector_data = sector_data.nlargest(10, 'value')
    
    fig = px.pie(sector_data, values='value', names='sector',
                 title="Структура торговли по секторам")
    
    fig.update_traces(hovertemplate='Сектор %{label}<br>%{value:,.0f} млн USD (%{percent:.1%})<extra></extra>')
    fig.update_layout(template="plotly_white")
    
    return fig

# Callback для географии торговли
@app.callback(
    Output("geography-map", "figure"),
    [Input("url", "pathname")]
)
def update_geography_map(pathname):
    # Группируем по регионам
    geography_data = trade_df.groupby('partnerName')['value'].sum().reset_index()
    geography_data = geography_data.nlargest(15, 'value')
    
    fig = px.bar(geography_data, x='value', y='partnerName', orientation='h',
                 title="География торговли (ТОП-15 партнеров)",
                 labels={'value': 'Объем торговли (млн USD)', 'partnerName': 'Страна/Регион'})
    
    fig.update_traces(hovertemplate='%{y}<br>%{x:,.0f} млн USD<extra></extra>')
    fig.update_layout(template="plotly_white")
    
    return fig

# Callback для ТОП-10 стран-партнеров
@app.callback(
    Output("top-partners", "figure"),
    [Input("url", "pathname")]
)
def update_top_partners(pathname):
    # Агрегируем данные за 2019-2023
    recent_years = [2019, 2020, 2021, 2022, 2023]
    recent_data = trade_df[trade_df['year'].isin(recent_years)]
    
    # Группируем по партнерам и типам потоков
    partner_data = recent_data.groupby(['partnerName', 'flow'])['value'].sum().reset_index()
    
    # Создаем сводную таблицу
    pivot_data = partner_data.pivot(index='partnerName', columns='flow', values='value').fillna(0)
    pivot_data['total'] = pivot_data['E'] + pivot_data['I']
    pivot_data['balance'] = pivot_data['E'] - pivot_data['I']
    
    # Топ-10 по общему объему
    top_partners = pivot_data.nlargest(10, 'total').reset_index()
    
    # Создаем график
    fig = go.Figure()
    
    # Добавляем бары для экспорта и импорта
    fig.add_trace(go.Bar(
        name='Экспорт',
        x=top_partners['partnerName'],
        y=top_partners['E'],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Импорт',
        x=top_partners['partnerName'],
        y=top_partners['I'],
        marker_color='lightcoral'
    ))
    
    # Добавляем линию сальдо
    colors = ['green' if x > 0 else 'red' for x in top_partners['balance']]
    fig.add_trace(go.Scatter(
        name='Сальдо',
        x=top_partners['partnerName'],
        y=top_partners['balance'],
        mode='markers+lines',
        marker=dict(color=colors, size=10),
        line=dict(color='yellow', width=2)
    ))
    
    fig.update_layout(
        title="ТОП-10 стран-партнеров (2019-2023)",
        barmode='group',
        template="plotly_white",
        xaxis_title="Страна",
        yaxis_title="Объем торговли (млн USD)"
    )
    
    fig.update_traces(hovertemplate='%{y:,.0f} млн USD<extra></extra>')
    
    return fig

# Callback для анализа России
@app.callback(
    Output("russia-analysis", "figure"),
    [Input("url", "pathname")]
)
def update_russia_analysis(pathname):
    # Данные по России
    russia_data = trade_df[trade_df['partnerName'] == 'Россия'].groupby(['year', 'flow'])['value'].sum().reset_index()
    
    # Переименовываем потоки
    flow_mapping = {'E': 'Экспорт', 'I': 'Импорт'}
    russia_data['flow'] = russia_data['flow'].map(flow_mapping)
    
    fig = px.line(russia_data, x='year', y='value', color='flow',
                  title="Торговля с Российской Федерацией",
                  labels={'value': 'Объем торговли (млн USD)', 'year': 'Год', 'flow': 'Тип потока'})
    
    fig.update_traces(hovertemplate='%{y:,.0f} млн USD<extra></extra>')
    fig.update_layout(template="plotly_white")
    
    return fig

# Callback для изменений структуры
@app.callback(
    Output("structure-changes", "figure"),
    [Input("url", "pathname")]
)
def update_structure_changes(pathname):
    # Сравниваем 2013 и 2023 годы
    years = [2013, 2023]
    structure_data = trade_df[trade_df['year'].isin(years)]
    
    # Группируем по товарным группам
    commodity_changes = structure_data.groupby(['year', 'commodityCode'])['value'].sum().reset_index()
    commodity_changes = commodity_changes.merge(commodities_df, left_on='commodityCode', right_on='id', how='left')
    
    # Создаем сводную таблицу
    pivot_changes = commodity_changes.pivot(index='text', columns='year', values='value').fillna(0)
    pivot_changes['change'] = ((pivot_changes[2023] - pivot_changes[2013]) / pivot_changes[2013] * 100)
    
    # Заменяем inf на 0 (возникает при делении на 0)
    pivot_changes.replace([np.inf, -np.inf], 0, inplace=True)
    pivot_changes.fillna(0, inplace=True)

    # Топ-10 изменений
    top_changes = pivot_changes.nlargest(10, 'change').reset_index()
    
    # Обрезаем названия
    top_changes['short_name'] = top_changes['text'].apply(
        lambda x: x[:30] + '...' if len(str(x)) > 30 else str(x)
    )
    
    # Создаем график
    fig = go.Figure()
    
    colors = ['green' if x > 0 else 'red' for x in top_changes['change']]
    
    fig.add_trace(go.Bar(
        x=top_changes['short_name'],
        y=top_changes['change'],
        marker_color=colors,
        text=[f"{x:+.1f} п.п." for x in top_changes['change']],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Изменения структуры торговли (2013-2023)",
        template="plotly_white",
        xaxis_title="Товарная группа",
        yaxis_title="Изменение доли (% п.п.)"
    )
    
    fig.update_traces(hovertemplate='%{x}<br>%{y:+.1f} п.п.<extra></extra>')
    
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050, host='0.0.0.0') 