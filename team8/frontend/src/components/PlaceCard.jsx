import RatingStars from './RatingStars'

function PlaceCard({ place, onSelect, active }) {
  return (
    <button
      className="card"
      style={{
        width: '100%',
        textAlign: 'right',
        borderColor: active ? 'rgba(74,194,154,0.8)' : undefined,
        background: active ? 'rgba(21,38,63,0.9)' : undefined,
      }}
      onClick={() => onSelect(place.place_id)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        <div style={{ fontWeight: 700, fontSize: 17 }}>{place.title}</div>
        <RatingStars value={place.average_rating || 0} size={14} />
      </div>
      <div style={{ color: '#9fb4d3', fontSize: 13, margin: '6px 0 10px' }}>
        {place.city_name} • {place.category_name || 'دسته‌بندی'}
      </div>
      <div style={{ color: '#d9e1ec', fontSize: 14, lineHeight: 1.6 }}>
        {place.description?.slice(0, 160) || 'بدون توضیح'}
      </div>
      <div className="list-inline" style={{ marginTop: 10 }}>
        <span className="pill-ghost">امتیاز {place.average_rating ? place.average_rating.toFixed(1) : 'جدید'}</span>
        <span className="pill-ghost">نظرات {place.rating_count || 0}</span>
      </div>
    </button>
  )
}

export default PlaceCard
