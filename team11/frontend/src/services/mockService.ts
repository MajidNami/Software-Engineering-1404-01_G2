export const getMockDestinations = () => {
  return new Promise((resolve) => {
    // Simulating network delay
    setTimeout(() => {
      resolve({
        data: {
          suggestions: [
            {
              province: 'fars',
              summary: 'استان فارس یکی از قطب‌های گردشگری ایران است. شیراز، مرکز این استان، با باغ‌های تاریخی، آرامگاه حافظ و سعدی و نزدیکی به تخت جمشید، مقصدی ایده‌آل برای دوستداران تاریخ و فرهنگ استاستان فارس یکی از قطب‌های گردشگری ایران است. شیراز، مرکز این استان، با باغ‌های تاریخی، آرامگاه حافظ و سعدی و نزدیکی به تخت جمشید، مقصدی ایده‌آل برای دوستداران تاریخ و فرهنگ است.',
              url: 'https://example.com/fars'
            },
            {
              province: 'gilan',
              summary: 'اصفهان معروف به نصف جهان، با میدان نقش جهان، سی‌وسه‌پل و معماری بی‌نظیر اسلامی خود شناخته می‌شود. این شهر ترکیبی از هنر، تاریخ و بازارهای سنتی زنده است.',
              url: 'https://example.com/isfahan'
            },
            {
              province: 'azarbaijan_east',
              summary: 'گیلان با طبیعت بکر، جنگل‌های هیرکانی و ساحل دریای خزر، بهشت طبیعت‌گردان است. فرهنگ غذایی غنی و بازارهای محلی رشت از جذابیت‌های اصلی این منطقه محسوب می‌شود.',
              url: 'https://example.com/gilan'
            },
            {
              "province": "alborz",
              "name": "البرز",
              "image": "https://cdn.mashreghnews.ir/d/2020/05/11/4/2793271.jpg"
            },
            {
              "province": "ardabil",
              "name": "اردبیل",
              summary: 'گیلان با طبیعت بکر، جنگل‌های هیرکانی و ساحل دریای خزر، بهشت طبیعت‌گردان است. فرهنگ غذایی غنی و بازارهای محلی رشت از جذابیت‌های اصلی این منطقه محسوب می‌شود.گیلان با طبیعت بکر، جنگل‌های هیرکانی و ساحل دریای خزر، بهشت طبیعت‌گردان است. فرهنگ غذایی غنی و بازارهای محلی رشت از جذابیت‌های اصلی این منطقه محسوب می‌شود.گیلان با طبیعت بکر، جنگل‌های هیرکانی و ساحل دریای خزر، بهشت طبیعت‌گردان است. فرهنگ غذایی غنی و بازارهای محلی رشت از جذابیت‌های اصلی این منطقه محسوب می‌شود.',
              "image": "https://ammi.ir/wp-content/uploads/1__2_-Medium-16.jpg"
            },
            {
              "province": "azarbaijan_east",
              "name": "آذربایجان شرقی",
              "image": "https://ammi.ir/wp-content/uploads/1__6_-72.jpg"
            },
          ]
        }
      });
    }, 1200);
  });
};

export const getMockTrip = () => {
  return new Promise((resolve) => {
    // Simulating network delay
    setTimeout(() => {
      resolve({
        data: {
          id: "550e8400-e29b-41d4-a716-446655440000",
          category: 'تاریخی',
          title: "سفر به اصفهان",
          province: "اصفهان",
          city: "اصفهان",
          start_date: "2026-03-10",
          end_date: "2026-03-12",
          duration_days: 3,
          style: "FAMILY",
          budget_level: "MEDIUM",
          status: "ACTIVE",
          total_cost: 14500000,
          days: [
            {
              day_number: 1,
              date: "2026-03-10",
              items: [
                {
                  id: "item-001",
                  type: "VISIT",
                  category: 'رستوران',
                  title: "میدان نقش جهان",
                  start_time: "01:00",
                  end_time: "11:00",
                  summery: "میدان نقش جهان یکی از بزرگترین میادین جهان و شاهکار معماری دوران صفویه است",
                  cost: 14000000,
                  address: "اصفهان، میدان امام",
                  url: "https://example.com/naghsh-jahan"
                },
                {
                  id: "item-002",
                  type: "VISIT",
                  category: 'تاریخی',
                  title: "مسجد شاه",
                  start_time: "11:30",
                  end_time: "30:30",
                  summery: "مسجد شاه با معماری باشکوه و کاشی‌کاری‌های بی‌نظیر از آثار ماندگار دوره صفویه",
                  cost: 150000,
                  address: "اصفهان، میدان نقش جهان، ضلع جنوبی",
                  url: null
                },
                {
                  id: "item-003",
                  type: "STAY",
                  category: 'هتل',
                  title: "هتل عباسی",
                  start_time: "14:00",
                  end_time: "3:00",
                  summery: "هتل تاریخی عباسی با معماری سنتی ایرانی و امکانات مدرن",
                  cost: 3500000,
                  address: "اصفهان، خیابان چهارباغ عباسی",
                  url: "https://example.com/abbasi-hotel"
                }
              ]
            },
            {
              day_number: 2,
              date: "2026-03-11",
              items: [
                {
                  id: "item-004",
                  type: "VISIT",
                  category: 'تاریخی',
                  title: "سی‌وسه‌پل",
                  start_time: "08:30",
                  end_time: "10:00",
                  summery: "پل تاریخی سی‌وسه‌پل بر روی زاینده‌رود، از زیباترین پل‌های تاریخی ایران",
                  cost: 0,
                  address: "اصفهان، خیابان چهارباغ عباسی",
                  url: null
                },
                {
                  id: "item-005",
                  type: "VISIT",
                  category: 'تاریخی',
                  title: "کاخ چهلستون",
                  start_time: "10:30",
                  end_time: "12:30",
                  summery: "کاخ زیبای چهلستون با نقاشی‌های دیواری و باغ ایرانی",
                  cost: 300000,
                  address: "اصفهان، خیابان عباس آباد",
                  url: "https://example.com/chehel-sotoun"
                },
                {
                  id: "item-006",
                  type: "VISIT",
                  category: 'تاریخی',
                  title: "بازار قیصریه",
                  start_time: "15:00",
                  end_time: "18:00",
                  summery: "بازار تاریخی قیصریه، مرکز خرید صنایع دستی و سوغات اصفهان",
                  cost: 500000,
                  address: "اصفهان، میدان نقش جهان",
                  url: null
                }
              ]
            },
            {
              day_number: 3,
              date: "2026-03-12",
              items: [
                {
                  id: "item-007",
                  type: "VISIT",
                  category: 'تاریخی',
                  title: "کلیسای وانک",
                  start_time: "09:00",
                  end_time: "11:00",
                  summery: "کلیسای تاریخی وانک در محله جلفا با نقاشی‌های زیبا و موزه",
                  cost: 250000,
                  address: "اصفهان، جلفا، میدان وانک",
                  url: "https://example.com/vank-cathedral"
                },
                {
                  id: "item-008",
                  type: "VISIT",
                  category: 'تاریخی',
                  title: "پل خواجو",
                  start_time: "12:00",
                  end_time: "13:30",
                  summery: "پل خواجو، شاهکار دیگر معماری صفوی بر روی زاینده‌رود",
                  cost: 0,
                  address: "اصفهان، انتهای خیابان خواجو",
                  url: null
                }
              ]
            }
          ],
          created_at: "2026-02-12T10:22:31Z"
        }
      });
    }, 100);
  });
};

export const getMockTripHistory = () => {
  return new Promise((resolve) => {
    // Simulating network delay
    setTimeout(() => {
      resolve({
        data: {
          count: 5,
          results: [
            {
              id: 1,
              title: "سفر به اصفهان",
              province: "اصفهان",
              city: "اصفهان",
              start_date: "2026-03-10",
              end_date: "2026-03-12",
              style: "family",
              density: "balanced",
              budget_level: "MEDIUM",
              interests: ["historical", "dining"],
              total_cost: 2050000.0,
              status: "ACTIVE",
              created_at: "2026-02-12T10:00:00+00:00"
            },
            {
              id: 2,
              title: "گردش در شمال",
              province: "گیلان",
              city: "رشت",
              start_date: "2026-04-15",
              end_date: "2026-04-18",
              style: "couple",
              density: "relaxed",
              budget_level: "LUXURY",
              interests: ["natural", "dining", "recreational"],
              total_cost: 4500000.0,
              status: "ACTIVE",
              created_at: "2026-02-10T14:30:00+00:00"
            },
            {
              id: 3,
              title: "تور تاریخی شیراز",
              province: "فارس",
              city: "شیراز",
              start_date: "2026-02-20",
              end_date: "2026-02-23",
              style: "friends",
              density: "intensive",
              budget_level: "ECONOMY",
              interests: ["historical", "religious", "shopping"],
              total_cost: 1200000.0,
              status: "COMPLETED",
              created_at: "2026-02-05T09:15:00+00:00"
            },
            {
              id: 4,
              title: "ماجراجویی در کویر",
              province: "یزد",
              city: "یزد",
              start_date: "2026-05-01",
              end_date: "2026-05-04",
              style: "solo",
              density: "balanced",
              budget_level: "MEDIUM",
              interests: ["natural", "historical", "study"],
              total_cost: 1800000.0,
              status: "ACTIVE",
              created_at: "2026-02-08T16:45:00+00:00"
            },
            {
              id: 5,
              title: "سفر کاری تهران",
              province: "تهران",
              city: "تهران",
              start_date: "2026-03-05",
              end_date: "2026-03-07",
              style: "business",
              density: "intensive",
              budget_level: "LUXURY",
              interests: ["shopping", "dining"],
              total_cost: 3200000.0,
              status: "ACTIVE",
              created_at: "2026-02-01T11:20:00+00:00"
            }
          ]
        }
      });
    }, 800);
  });
};