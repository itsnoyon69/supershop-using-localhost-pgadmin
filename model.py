from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime

def customer_segmentation(df):

    today = datetime.today()

    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (today - x.max()).days,
        'order_id': 'count',
        'total_price': 'sum'
    })

    rfm.columns = ['recency','frequency','monetary']

    scaler = StandardScaler()
    scaled = scaler.fit_transform(rfm)

    kmeans = KMeans(n_clusters=3)
    rfm['cluster'] = kmeans.fit_predict(scaled)

    return rfm