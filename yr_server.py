import json
import ssl
import urllib.request
from fastmcp import FastMCP

mcp = FastMCP("YR-Weather")

def fetch_yr_data(lat: float, lon: float) -> dict:
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={round(lat, 4)}&lon={round(lon, 4)}"
    headers = {"User-Agent": "KyunginWeatherApp/1.0 (kyungin@gmail.com)"}
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=context) as response:
        return json.loads(response.read().decode('utf-8'))

@mcp.tool()
def get_weather(latitude: float, longitude: float) -> str:
    """위도와 경도를 입력받아 현재 날씨 및 향후 24시간 날씨 예보 요약을 가져옵니다."""
    try:
        data = fetch_yr_data(latitude, longitude)
        timeseries = data["properties"]["timeseries"]
        current = timeseries[0]["data"]["instant"]["details"]
        current_temp = current.get("air_temperature", "N/A")
        current_wind = current.get("wind_speed", "N/A")
        current_humidity = current.get("relative_humidity", "N/A")
        
        symbol = "정보없음"
        if "next_1_hours" in timeseries[0]["data"]:
            symbol = timeseries[0]["data"]["next_1_hours"]["summary"].get("symbol_code", "정보없음")
            
        result = [
            f"=== 현재 날씨 (위도 {latitude}, 경도 {longitude}) ===",
            f"- 상태: {symbol}",
            f"- 기온: {current_temp}°C",
            f"- 습도: {current_humidity}%",
            f"- 풍속: {current_wind} m/s\n",
            "=== 향후 주요 시간대별 예보 ==="
        ]
        
        for idx in [3, 6, 12, 18, 24]:
            if idx < len(timeseries):
                item = timeseries[idx]
                time_utc = item["time"].replace("Z", "").split("T")
                date_part, time_part = time_utc[0][5:], time_utc[1][:5]
                temp = item["data"]["instant"]["details"].get("air_temperature", "N/A")
                f_symbol = ""
                if "next_1_hours" in item["data"]:
                    f_symbol = item["data"]["next_1_hours"]["summary"].get("symbol_code", "")
                elif "next_6_hours" in item["data"]:
                    f_symbol = item["data"]["next_6_hours"]["summary"].get("symbol_code", "")
                result.append(f"- [{date_part} {time_part} UTC] 상태: {f_symbol} | 기온: {temp}°C")
                
        return "\n".join(result)
    except Exception as e:
        return f"날씨 정보 조회 실패: {str(e)}"

@mcp.tool()
def get_weekly_forecast(latitude: float, longitude: float) -> str:
    """위도와 경도를 입력받아 향후 며칠간의 일별 날씨 예보 데이터를 가져옵니다."""
    try:
        data = fetch_yr_data(latitude, longitude)
        timeseries = data["properties"]["timeseries"]
        result = [f"=== 주간 예보 (위도 {latitude}, 경도 {longitude}) ==="]
        for i in range(0, min(len(timeseries), 120), 24):
            item = timeseries[i]
            date_part = item["time"].split("T")[0]
            details = item["data"]["instant"]["details"]
            result.append(f"- {date_part}: 기온 {details.get('air_temperature', 'N/A')}°C | 풍속 {details.get('wind_speed', 'N/A')} m/s")
        return "\n".join(result)
    except Exception as e:
        return f"주간 예보 조회 실패: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
