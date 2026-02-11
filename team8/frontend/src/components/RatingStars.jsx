function RatingStars({ value = 0, size = 18 }) {
  const stars = Array.from({ length: 5 }, (_, i) => i + 1)
  return (
    <div className="rating" aria-label={`امتیاز ${value} از 5`}>
      {stars.map((s) => (
        <span key={s} style={{ fontSize: size }}>
          {value >= s ? '★' : value >= s - 0.5 ? '⯨' : '☆'}
        </span>
      ))}
    </div>
  )
}

export default RatingStars
