from google.analytics.data_v1beta import BetaAnalyticsDataClient
import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt


from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Filter
from google.analytics.data_v1beta.types import FilterExpression
from google.analytics.data_v1beta.types import FilterExpressionList
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest

"""
class: Google Analytics4 Report
see doc https://developers.google.com/analytics/devguides/reporting/data/v1/basics
"""
class GoogleAnalytics4Report:
    def __init__(self, propertyId):
        self._propertyId = propertyId
        self._metrics = []
        self._dimensions = []
        self._dateRange = ['28daysAgo', 'yesterday']
        self._filters = None
        self._result = []

    def setMetrics(self, metrics):
        """setter for report metrics."""
        self._metrics = metrics
        return self

    def setDimensions(self, dimensions):
        """setter for report dimensions."""
        self._dimensions = dimensions
        return self

    def setDateRange(self, dateRange):
        """setter for date range."""
        self._dateRange = dateRange
        return self

    def setFilters(self, **kwargs):
        """setter for report filters."""
        self._filters = kwargs
        return self

    def run(self, client):
        """Run this report on a Data API(GA4)."""

        def filterExprBuilder(filters):
            if isinstance(filters, list):
                return FilterExpressionList(expressions=[FilterExpression(filter=filter) for filter in filters])
            return FilterExpression(filter=filters)

        dimension_filter = None
        if self._filters is not None:
            dimension_filter = FilterExpression(
                **dict(map(lambda filter: (filter[0], filterExprBuilder(filter[1]) if filter[0] != 'filter' else filter[1]), self._filters.items()))
            )

        request = RunReportRequest(
            property=f"properties/{self._propertyId}",
            metrics=[Metric(name=name) for name in self._metrics],
            dimensions=[Dimension(name=name) for name in self._dimensions],
            date_ranges=[DateRange(start_date=self._dateRange[0], end_date=self._dateRange[1])],
            dimension_filter=dimension_filter
        )

        response = client.run_report(request)
        print(f"{response.row_count} rows received")
        self._result = [self._parseRow(row) for row in response.rows]
        return self

    def getResult(self):
        """get result returned by Data API(GA4)."""
        return self._result

    def getRecords(self):
        """get result as a list of record."""
        columns = [('dimensions', col) for col in self._dimensions]
        columns.extend([('metrics', col) for col in self._metrics])
        return [dict([(name, item[i][name]) for i, name in columns]) for item in self._result]

    def _parseRow(self, row):
      dimensions = self._dimensions
      metrics = self._metrics

      return {
          'dimensions':dict([(name, row.dimension_values[i].value) for i, name in enumerate(self._dimensions)]),
          'metrics':dict([(name, float(row.metric_values[i].value)) for i, name in enumerate(self._metrics)])
          }






# アカウント設定
# credential.jsonを/credentialに設置 && GA4 プロパティIDを設定
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/credential.json'
# private key

GA_PROPERTY_ID = 416986327


client = BetaAnalyticsDataClient()


# Top viewed pages
topPagesReport = GoogleAnalytics4Report(GA_PROPERTY_ID).setDimensions(
    dimensions=['pagePath']
).setMetrics(
    metrics=['screenPageViews']
).setDateRange(
    dateRange=['356daysAgo', 'yesterday']
).run(client)

# データフレームに加工
df = pd.DataFrame.from_records(topPagesReport.getRecords())
df = df.sort_values('screenPageViews', ascending=False)
print(df)

# only /posts/+
df = df[df['pagePath'].str.contains('/posts/')]
# remove  /posts/ from pagePath
df['pagePath'] = df['pagePath'].str.replace('/posts/', '')
# remove *.html
df['pagePath'] = df['pagePath'].str.replace('.html', '')
# extract parent directory
df['pagePath'] = df['pagePath'].str.extract(r'(.*)/')
# remove nan
df = df.dropna()
# remove pagePath duplicates
df = df.drop_duplicates(subset='pagePath')
print(df)

# save as csv
df.to_csv('ranking.csv', index=False)