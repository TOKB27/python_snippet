def add(a, b):
  return a + b

class WeatherAPI:
  def get_temperature(self, city):
      # 本来なら外部API呼び出し（ここはテスト対象外）
      raise NotImplementedError("This should call an external API")

def get_weather_message(city, api: WeatherAPI):
  temp = api.get_temperature(city)
  if temp >= 30:
      return f"{city}は暑いです（{temp}℃）"
  else:
      return f"{city}は快適です（{temp}℃）"