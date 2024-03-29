from bs4 import BeautifulSoup
from charting.models import BondYield
from datetime import datetime
from django.core.management.base import BaseCommand
import requests


TREASURY_URL = 'https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData'


def get_field(content, field):
  value = content.find(field).get_text()
  if value != '':
    return float(value)
  return None


class Command(BaseCommand):
  help = 'Scrapes the treasury.gov website for new bond yield data.'
  
  def add_arguments(self, parser):
    pass
  
  def handle(self, *args, **options):
    data = requests.get(TREASURY_URL)
    rss_feed = BeautifulSoup(data.text, features='xml')
    
    contents = rss_feed.find_all('content')
    bonds = []
    for content in contents:      
      bond_yield = BondYield()
      bond_yield.date = datetime.strptime(content.find('NEW_DATE').get_text(), '%Y-%m-%dT00:00:00')
      bond_yield.one_month = get_field(content, 'd:BC_1MONTH')
      bond_yield.two_month = get_field(content, 'd:BC_2MONTH')
      bond_yield.three_month = get_field(content, 'd:BC_3MONTH')
      bond_yield.six_month = get_field(content, 'd:BC_6MONTH')
      bond_yield.one_year = get_field(content, 'd:BC_1YEAR')
      bond_yield.two_year = get_field(content, 'd:BC_2YEAR')
      bond_yield.three_year = get_field(content, 'd:BC_3YEAR')
      bond_yield.five_year = get_field(content, 'd:BC_5YEAR')
      bond_yield.seven_year = get_field(content, 'd:BC_7YEAR')
      bond_yield.ten_year = get_field(content, 'd:BC_10YEAR')
      bond_yield.twenty_year = get_field(content, 'd:BC_20YEAR')
      bond_yield.thirty_year = get_field(content, 'd:BC_30YEAR')
      bonds.append(bond_yield)

    # Sort the bonds by date and insert them into the database accordingly.
    bonds.sort(key=lambda x: x.date)
    for b in bonds:
      try:
        bond = BondYield.objects.get(date=b.date)
      except BondYield.DoesNotExist:
        b.save()

    print (len(bonds), 'bonds added.')
