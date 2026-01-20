# MeasuresRouter.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from DataBase.database import get_session
from DataBase.models import Measures, Values
from DataBase.schemas import MeasureCreate, MeasureRead, MeasureUpdate, MeasureDelete
from Routers.crud import create_unit, get_all_units, delete_unit

from typing import List
import json
from datetime import datetime

measures_router = APIRouter(prefix="/measures", tags=["Measures"])


# CREATE
@measures_router.post("/create", response_model=MeasureRead)
async def create_measure(measure: MeasureCreate, session: AsyncSession = Depends(get_session)):
    return await create_unit(measure, Measures, session)


# GET ALL
@measures_router.get("/get_all", response_model=list[MeasureRead])
async def get_all_measures(session: AsyncSession = Depends(get_session)):
    return await get_all_units(Measures, session)


# GET BY VALUE ID
@measures_router.get("/get_by_value_id/{value_id}", response_model=list[MeasureRead])
async def get_by_value_id(value_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Measures).where(Measures.valueId == value_id))
    measures = result.scalars().all()
    if not measures:
        value_result = await session.execute(select(Values).where(Values.id == value_id))
        value_unit = value_result.scalar_one_or_none()
        if not value_unit:
            raise HTTPException(status_code=404, detail=f"Value with id {value_id} not found")
        raise HTTPException(status_code=404, detail=f"No measures found for value {value_unit.name}")
    return measures


# DELETE
@measures_router.delete("/delete/{measure_id}")
async def delete_measure(measure_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await delete_unit(Measures, measure_id, session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Measure not found")


# ГЕНЕРАЦІЯ ГРАФІКА - ПОВЕРТАЄ ГОТОВУ HTML СТОРІНКУ
@measures_router.get("/chart", response_class=HTMLResponse)
async def generate_chart(
        value_ids: str = Query(..., description="Comma-separated list of value IDs"),
        start_time: int = Query(..., description="Start time in Unix timestamp"),
        end_time: int = Query(..., description="End time in Unix timestamp"),
        session: AsyncSession = Depends(get_session)
):
    """
    Генерує готову HTML сторінку з графіком з автоматичною оптимізацією
    """

    try:
        # Парсимо ID значень
        try:
            ids = [int(id.strip()) for id in value_ids.split(',')]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid value IDs format: {str(e)}")

        if not ids:
            raise HTTPException(status_code=400, detail="No value IDs provided")

        # Збираємо дані для кожного value_id
        datasets = []

        for value_id in ids:
            try:
                # Отримуємо інформацію про Value
                value_result = await session.execute(select(Values).where(Values.id == value_id))
                value = value_result.scalar_one_or_none()

                if not value:
                    continue

                # Отримуємо виміри в заданому часовому проміжку
                measures_result = await session.execute(
                    select(Measures)
                    .where(
                        and_(
                            Measures.valueId == value_id,
                            Measures.measureTime >= start_time,
                            Measures.measureTime <= end_time
                        )
                    )
                    .order_by(Measures.measureTime)
                )
                measures = measures_result.scalars().all()

                if not measures:
                    continue

                datasets.append({
                    "label": value.name,
                    "tag": value.tag if value.tag else "N/A",
                    "data": [
                        {"x": int(m.measureTime) * 1000, "y": float(m.measureValue)}
                        for m in measures
                    ]
                })

            except Exception:
                continue

        if not datasets:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")

        # Генеруємо HTML
        html = generate_chart_html(datasets, start_time, end_time)

        return HTMLResponse(content=html)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def generate_chart_html(datasets: list, start_time: int, end_time: int) -> str:
    """
    Генерує HTML сторінку з графіком, оптимізовану для перегляду та друку на А4 landscape
    """

    # Кольори для різних ліній
    colors = [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 206, 86)',
        'rgb(75, 192, 192)',
        'rgb(153, 102, 255)',
        'rgb(255, 159, 64)',
        'rgb(199, 199, 199)',
        'rgb(83, 102, 255)',
        'rgb(255, 99, 255)',
        'rgb(99, 255, 132)'
    ]

    for idx, dataset in enumerate(datasets):
        color = colors[idx % len(colors)]
        dataset['borderColor'] = color
        dataset['backgroundColor'] = color.replace('rgb', 'rgba').replace(')', ', 0.1)')
        dataset['tension'] = 0.1
        dataset['pointRadius'] = 0
        dataset['pointHoverRadius'] = 0
        dataset['borderWidth'] = 2

    datasets_json = json.dumps(datasets)

    start_dt = datetime.fromtimestamp(start_time).strftime('%d.%m.%Y %H:%M')
    end_dt = datetime.fromtimestamp(end_time).strftime('%d.%m.%Y %H:%M')

    html = f"""
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Графік вимірів</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .chart-container {{
            padding: 30px 40px;
            position: relative;
            height: 70vh;
        }}

        .info {{
            padding: 20px 40px;
            background: #f8f9fa;
            border-top: 2px solid #e9ecef;
        }}

        .info h3 {{
            margin-bottom: 15px;
            color: #333;
        }}

        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}

        .print-btn {{
            display: inline-block;
            margin: 20px 40px;
            padding: 12px 25px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }}

        .print-btn:hover {{
            background: #218838;
        }}

        /* Прибираємо зайві заголовки вікна браузера при друці */
        @media print {{
            @page {{
                size: A4 landscape;
                margin: 8mm 10mm;
            }}

            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
                background: white !important;
                color: black !important;
            }}

            .container {{
                box-shadow: none;
                border-radius: 0;
                max-width: none;
                width: 100%;
                background: white;
                page-break-inside: avoid;
            }}

            .header {{
                background: white !important;
                color: black !important;
                padding: 6mm 8mm 4mm !important;
                border-bottom: 1px solid #444;
            }}

            .header h1 {{
                font-size: 18pt !important;
                margin: 0 0 4mm 0 !important;
            }}

            .header p {{
                font-size: 11pt !important;
                margin: 0;
                color: #333 !important;
            }}

            .chart-container {{
                padding: 4mm 8mm 8mm !important;
                height: 135mm !important;
                page-break-inside: avoid !important;
            }}

            .chart-container canvas {{
                max-height: 100% !important;
                width: 100% !important;
            }}

            .info {{
                padding: 4mm 8mm !important;
                background: white !important;
                border-top: 1px solid #666;
                page-break-before: avoid;
                font-size: 9pt !important;
            }}

            .info h3 {{
                font-size: 12pt !important;
                margin: 0 0 3mm 0 !important;
            }}

            .legend {{
                font-size: 9pt !important;
                gap: 12px !important;
            }}

            .legend-item {{
                white-space: nowrap;
            }}

            .legend-color {{
                width: 14px !important;
                height: 14px !important;
            }}

            .print-btn {{
                display: none !important;
            }}
        }}

        /* Mobile responsive styles */
        @media screen and (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .container {{
                border-radius: 10px;
            }}

            .header {{
                padding: 20px 15px;
            }}

            .header h1 {{
                font-size: 1.5em;
                margin-bottom: 8px;
            }}

            .header p {{
                font-size: 0.85em;
            }}

            .chart-container {{
                padding: 15px;
                height: 50vh;
                min-height: 300px;
            }}

            .info {{
                padding: 15px;
            }}

            .info h3 {{
                font-size: 1em;
                margin-bottom: 10px;
            }}

            .legend {{
                gap: 10px;
                font-size: 0.85em;
            }}

            .legend-item {{
                gap: 8px;
            }}

            .legend-color {{
                width: 16px;
                height: 16px;
            }}

            .print-btn {{
                margin: 15px;
                padding: 10px 20px;
                font-size: 0.9em;
                width: calc(100% - 30px);
            }}
        }}

        @media screen and (max-width: 480px) {{
            .header h1 {{
                font-size: 1.2em;
            }}

            .header p {{
                font-size: 0.75em;
            }}

            .chart-container {{
                padding: 10px;
                height: 40vh;
            }}

            .info h3 {{
                font-size: 0.9em;
            }}

            .legend {{
                font-size: 0.75em;
                gap: 8px;
            }}

            .legend-color {{
                width: 14px;
                height: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Графік вимірів</h1>
            <p>Часовий проміжок: {start_dt} - {end_dt}</p>
        </div>

        <div class="chart-container">
            <canvas id="myChart"></canvas>
        </div>

        <div class="info">
            <h3>📈 Відображені значення:</h3>
            <div class="legend" id="legend"></div>
        </div>

        <button onclick="window.print()" class="print-btn">🖨️ Друк / Зберегти як PDF</button>
    </div>

    <script>
        const datasets = {datasets_json};

        const ctx = document.getElementById('myChart').getContext('2d');
        const myChart = new Chart(ctx, {{
            type: 'line',
            data: {{
                datasets: datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                layout: {{
                    padding: {{
                        left: 12,
                        right: 30,
                        top: 20,
                        bottom: 20
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    intersect: false,
                    axis: 'x'
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{
                            font: {{ size: 13, weight: 'bold' }},
                            padding: 16,
                            boxWidth: 20,
                            usePointStyle: true
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            title: function(context) {{
                                const date = new Date(context[0].parsed.x);
                                return date.toLocaleString('uk-UA', {{
                                    timeZone: 'Europe/Kiev',
                                    year: 'numeric',
                                    month: '2-digit',
                                    day: '2-digit',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    second: '2-digit'
                                }});
                            }},
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(2);
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'hour',
                            displayFormats: {{
                                hour: 'HH:mm',
                                day: 'dd.MM'
                            }},
                            tooltipFormat: 'dd.MM.yyyy HH:mm:ss'
                        }},
                        title: {{
                            display: true,
                            text: 'Час',
                            font: {{ size: 14, weight: 'bold' }}
                        }},
                        ticks: {{
                            maxRotation: 45,
                            minRotation: 45,
                            autoSkip: true,
                            maxTicksLimit: 16
                        }},
                        grid: {{
                            color: 'rgba(0,0,0,0.12)'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Значення',
                            font: {{ size: 14, weight: 'bold' }}
                        }},
                        ticks: {{
                            precision: 1,
                            stepSize: 0.5,
                            maxTicksLimit: 12
                        }},
                        grid: {{
                            color: 'rgba(0,0,0,0.12)'
                        }}
                    }}
                }}
            }}
        }});

        const legendDiv = document.getElementById('legend');
        datasets.forEach(dataset => {{
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `
                <div class="legend-color" style="background-color: ${{dataset.borderColor}}"></div>
                <span><strong>${{dataset.label}}</strong> (${{dataset.data.length}} точок)</span>
            `;
            legendDiv.appendChild(item);
        }});
    </script>
</body>
</html>
"""
    return html