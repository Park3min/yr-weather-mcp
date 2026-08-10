import json
import ssl
import urllib.request
from collections import defaultdict
from fastmcp import FastMCP

mcp = FastMCP("YR-Weather")

def fetch_yr_data(lat: float, lon: float) -> dict:
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={round(lat, 4)}&lon={round(lon, 4)}"
    headers = {"User-Agent": "KyunginWeatherApp/1.0 (kyungin@gmail.com)"}
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=context) as response:
        return json.loads(response.read().decode("utf-8"))

@mcp.tool()
def get_weather(latitude: float, longitude: float) -> str:
    """위도와 경도를 입력받아 현재 날씨 및 향후 24시간의 시간대별 상세 날씨 예보를 가져옵니다."""
    try:
        data = fetch_yr_data(latitude, longitude)
        timeseries = data["properties"]["timeseries"]
        current = timeseries[0]["data"]["instant"]["details"]
        
        symbol = "정보없음"
        if "next_1_hours" in timeseries[0]["data"]:
            symbol = timeseries[0]["data"]["next_1_hours"]["summary"].get("symbol_code", "정보없음")
            
        result = [
            f"=== 현재 날씨 (위도 {latitude}, 경도 {longitude}) ===",
            f"- 상태: {symbol}",
            f"- 기온: {current.get("air_temperature", "N/A")}°C",
            f"- 습도: {current.get("relative_humidity", "N/A")}%",
            f"- 풍속: {current.get("wind_speed", "N/A")} m/s\n",
            "=== 향후 24시간 시간대별 상세 예보 ==="
        ]
        
        for item in timeseries[:24]:
            time_utc = item["time"].replace("Z", "").split("T")
            date_part, time_part = time_utc[0][5:], time_utc[1][:5]
            details = item["data"]["instant"]["details"]
            temp = details.get("air_temperature", "N/A")
            humidity = details.get("relative_humidity", "N/A")
            wind = details.get("wind_speed", "N/A")
            
            f_symbol = ""
            if "next_1_hours" in item["data"]:
                f_symbol = item["data"]["next_1_hours"]["summary"].get("symbol_code", "")
            elif "next_6_hours" in item["data"]:
                f_symbol = item["data"]["next_6_hours"]["summary"].get("symbol_code", "")
                
            result.append(f"- [{date_part} {time_part} UTC] 기온: {temp}°C | 습도: {humidity}% | 풍속: {wind}m/s | 상태: {f_symbol}")
                
        return "\n".join(result)
    except Exception as e:
        return f"날씨 정보 조회 실패: {str(e)}"

@mcp.tool()
def get_weekly_forecast(latitude: float, longitude: float) -> str:
    """위도와 경도를 입력받아 향후 일별 최저/최고 기온 및 풍속 범위를 분석하여 반환합니다."""
    try:
        data = fetch_yr_data(latitude, longitude)
        timeseries = data["properties"]["timeseries"]
        
        daily_map = defaultdict(list)
        for item in timeseries:
            date_part = item["time"].split("T")[0]
            details = item["data"]["instant"]["details"]
            temp = details.get("air_temperature")
            wind = details.get("wind_speed")
            humidity = details.get("relative_humidity")
            if temp is not None:
                daily_map[date_part].append({
                    "temp": temp,
                    "wind": wind,
                    "humidity": humidity
                })
        
        result = [f"=== 주간 일별 종합 예보 (위도 {latitude}, 경도 {longitude}) ==="]
        for date_str, entries in daily_map.items():
            temps = [e["temp"] for e in entries if e["temp"] is not None]
            winds = [e["wind"] for e in entries if e["wind"] is not None]
            
            min_t, max_t = min(temps), max(temps)
            min_w, max_w = min(winds), max(winds)
            
            result.append(f"- {date_str}: 최저 {min_t}°C / 최고 {max_t}°C | 풍속 {min_w}~{max_w} m/s (예보 데이터 {len(entries)}개 수집됨)")
            
        return "\n".join(result)
    except Exception as e:
        return f"주간 예보 조회 실패: {str(e)}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
