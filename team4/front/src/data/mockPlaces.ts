export interface Place {
  id: string;
  name: string;
  category: string;
  latitude: number;
  longitude: number;
  rating: number;
  address: string;
  description: string;
  images: string[];
  reviews: Review[];
}

export interface Review {
  id: string;
  author: string;
  rating: number;
  comment: string;
  date: string;
}

export const mockPlaces: Place[] = [
  {
    id: 'place-1',
    name: 'The Grand Hotel',
    category: 'hotel',
    latitude: 40.7589,
    longitude: -73.9851,
    rating: 4.5,
    address: '123 Park Avenue, New York, NY',
    description: 'Luxurious hotel in the heart of Manhattan with stunning city views.',
    images: [
      'https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/271624/pexels-photo-271624.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-1',
        author: 'John Smith',
        rating: 5,
        comment: 'Amazing stay! The service was impeccable and the rooms were spotless.',
        date: '2024-01-15',
      },
      {
        id: 'rev-2',
        author: 'Sarah Johnson',
        rating: 4,
        comment: 'Great location and comfortable rooms. Would definitely recommend.',
        date: '2024-01-20',
      },
    ],
  },
  {
    id: 'place-2',
    name: 'Bella Vista Restaurant',
    category: 'restaurant',
    latitude: 40.7614,
    longitude: -73.9776,
    rating: 4.7,
    address: '456 Madison Avenue, New York, NY',
    description: 'Fine dining Italian restaurant with authentic cuisine.',
    images: [
      'https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/1581384/pexels-photo-1581384.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-3',
        author: 'Michael Brown',
        rating: 5,
        comment: 'Best Italian food in the city! The pasta was perfect.',
        date: '2024-01-18',
      },
      {
        id: 'rev-4',
        author: 'Emily Davis',
        rating: 4,
        comment: 'Wonderful atmosphere and delicious food. A bit pricey but worth it.',
        date: '2024-01-22',
      },
    ],
  },
  {
    id: 'place-3',
    name: 'Central Park',
    category: 'park',
    latitude: 40.7829,
    longitude: -73.9654,
    rating: 4.9,
    address: 'Central Park, New York, NY',
    description: 'Iconic urban park offering green spaces, walking paths, and recreational activities.',
    images: [
      'https://images.pexels.com/photos/1105766/pexels-photo-1105766.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/380782/pexels-photo-380782.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-5',
        author: 'Lisa Anderson',
        rating: 5,
        comment: 'Beautiful park! Perfect for morning jogs and picnics.',
        date: '2024-01-16',
      },
      {
        id: 'rev-6',
        author: 'David Wilson',
        rating: 5,
        comment: 'A must-visit in NYC. So peaceful and well-maintained.',
        date: '2024-01-19',
      },
    ],
  },
  {
    id: 'place-4',
    name: 'Museum of Modern Art',
    category: 'museum',
    latitude: 40.7614,
    longitude: -73.9776,
    rating: 4.6,
    address: '11 West 53rd Street, New York, NY',
    description: 'World-renowned museum featuring contemporary and modern art.',
    images: [
      'https://images.pexels.com/photos/1109197/pexels-photo-1109197.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/2883049/pexels-photo-2883049.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-7',
        author: 'James Taylor',
        rating: 5,
        comment: 'Incredible collection! Spent hours exploring the exhibits.',
        date: '2024-01-14',
      },
      {
        id: 'rev-8',
        author: 'Maria Garcia',
        rating: 4,
        comment: 'Great museum with diverse artwork. Can get crowded on weekends.',
        date: '2024-01-21',
      },
    ],
  },
  {
    id: 'place-5',
    name: 'Coffee Haven',
    category: 'cafe',
    latitude: 40.7489,
    longitude: -73.9680,
    rating: 4.3,
    address: '789 Lexington Avenue, New York, NY',
    description: 'Cozy coffee shop with artisanal brews and fresh pastries.',
    images: [
      'https://images.pexels.com/photos/1307698/pexels-photo-1307698.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/2788792/pexels-photo-2788792.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-9',
        author: 'Robert Martinez',
        rating: 4,
        comment: 'Great coffee and friendly staff. Perfect spot for working remotely.',
        date: '2024-01-17',
      },
      {
        id: 'rev-10',
        author: 'Jennifer Lee',
        rating: 5,
        comment: 'My favorite coffee shop! The lattes are amazing.',
        date: '2024-01-23',
      },
    ],
  },
  {
    id: 'place-6',
    name: 'Broadway Theater',
    category: 'theater',
    latitude: 40.7580,
    longitude: -73.9855,
    rating: 4.8,
    address: '234 West 44th Street, New York, NY',
    description: 'Historic theater showcasing world-class Broadway productions.',
    images: [
      'https://images.pexels.com/photos/109669/pexels-photo-109669.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/713149/pexels-photo-713149.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-11',
        author: 'Thomas White',
        rating: 5,
        comment: 'Incredible performance! The acoustics and seating were perfect.',
        date: '2024-01-12',
      },
      {
        id: 'rev-12',
        author: 'Amanda Harris',
        rating: 5,
        comment: 'Best theater experience ever. Highly recommend!',
        date: '2024-01-24',
      },
    ],
  },
  {
    id: 'place-7',
    name: 'Fitness Plus Gym',
    category: 'gym',
    latitude: 40.7505,
    longitude: -73.9934,
    rating: 4.2,
    address: '567 8th Avenue, New York, NY',
    description: 'State-of-the-art fitness center with personal trainers and group classes.',
    images: [
      'https://images.pexels.com/photos/1552242/pexels-photo-1552242.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/1552252/pexels-photo-1552252.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-13',
        author: 'Kevin Clark',
        rating: 4,
        comment: 'Good equipment and clean facilities. Membership is reasonable.',
        date: '2024-01-13',
      },
      {
        id: 'rev-14',
        author: 'Nicole Robinson',
        rating: 4,
        comment: 'Love the yoga classes! Great instructors.',
        date: '2024-01-25',
      },
    ],
  },
  {
    id: 'place-8',
    name: 'Urban Shopping Center',
    category: 'shopping',
    latitude: 40.7549,
    longitude: -73.9840,
    rating: 4.4,
    address: '890 5th Avenue, New York, NY',
    description: 'Premier shopping destination with designer brands and boutiques.',
    images: [
      'https://images.pexels.com/photos/264549/pexels-photo-264549.jpeg?auto=compress&cs=tinysrgb&w=800',
      'https://images.pexels.com/photos/1884584/pexels-photo-1884584.jpeg?auto=compress&cs=tinysrgb&w=800',
    ],
    reviews: [
      {
        id: 'rev-15',
        author: 'Patricia Lewis',
        rating: 4,
        comment: 'Great variety of stores. Can be crowded during weekends.',
        date: '2024-01-11',
      },
      {
        id: 'rev-16',
        author: 'Christopher Walker',
        rating: 5,
        comment: 'Excellent shopping experience with helpful staff.',
        date: '2024-01-26',
      },
    ],
  },
];

export const categories = [
  { id: 'all', name: 'همه', icon: 'MapPin' },
  { id: 'hotel', name: 'هتل', icon: 'Building' },
  { id: 'restaurant', name: 'رستوران', icon: 'Utensils' },
  { id: 'hospital', name: 'بیمارستان', icon: 'Hospital' },
  { id: 'shopping', name: 'مرکز خرید', icon: 'ShoppingBag' },
  { id: 'museum', name: 'موزه', icon: 'Landmark' },
  { id: 'cafe', name: 'کافه', icon: 'Coffee' },
  { id: 'pharmacy', name: 'داروخانه', icon: 'Pill' },
  { id: 'clinic', name: 'درمانگاه', icon: 'Stethoscope' },
];
