import pytest
from target_code import add, get_weather_message

def test_add():
  assert add(2, 3) == 5
  assert add(-1, 1) == 0

# 自前で作るスタブ（モック）
class FakeWeatherAPI:
  def __init__(self, temp):
      self._temp = temp

  def get_temperature(self, city):
      return self._temp

def test_get_weather_message_hot():
  fake_api = FakeWeatherAPI(temp=35)
  message = get_weather_message("東京", fake_api)
  assert message == "東京は暑いです（35℃）"

def test_get_weather_message_cool():
  fake_api = FakeWeatherAPI(temp=22)
  message = get_weather_message("札幌", fake_api)
  assert message == "札幌は快適です（22℃）"