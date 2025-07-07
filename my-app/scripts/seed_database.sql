-- Insert sample destinations
INSERT INTO destinations (name, slug, description, long_description, image_url, rating, review_count, region, destination_type, best_season, highlights, latitude, longitude, entry_fee, facilities) VALUES
('Sigiriya', 'sigiriya', 'Ancient rock fortress rising 200m above the jungle', 'Sigiriya, also known as Lion Rock, is an ancient rock fortress located in the northern Matale District near the town of Dambulla. It is a UNESCO World Heritage Site and one of the most visited tourist destinations in Sri Lanka.', '/images/sigiriya.jpg', 4.9, 2847, 'Central', 'Cultural', 'Year-round', ARRAY['Ancient frescoes', 'Lion''s Gate', 'Summit views', 'Water gardens'], 7.9569, 80.7603, 30.00, ARRAY['Parking', 'Restrooms', 'Guide services', 'Museum']),

('Mirissa', 'mirissa', 'Pristine beach perfect for whale watching', 'Mirissa is a small town on the south coast of Sri Lanka, located in the Matara District of the Southern Province. It is approximately 150 kilometres south of Colombo and is situated at an elevation of 4 metres above sea level.', '/images/mirissa.jpg', 4.8, 1923, 'Southern', 'Beach', 'Nov-Apr', ARRAY['Blue whales', 'Golden beaches', 'Coconut Hill', 'Surfing'], 5.9487, 80.4707, 0.00, ARRAY['Beach access', 'Restaurants', 'Water sports', 'Accommodation']),

('Ella', 'ella', 'Hill station with tea plantations and waterfalls', 'Ella is a small town in the Badulla District of Uva Province, Sri Lanka governed by an Urban Council. It is approximately 200 kilometres east of Colombo and is situated at an elevation of 1,041 metres above sea level.', '/images/ella.jpg', 4.9, 3156, 'Central', 'Nature', 'Year-round', ARRAY['Nine Arch Bridge', 'Little Adam''s Peak', 'Tea estates', 'Ravana Falls'], 6.8667, 81.0467, 0.00, ARRAY['Hiking trails', 'Viewpoints', 'Tea factories', 'Restaurants']),

('Kandy', 'kandy', 'Cultural capital with the sacred Temple of the Tooth', 'Kandy is a major city in Sri Lanka located in the Central Province. It was the last capital of the ancient kings'' era of Sri Lanka. The city lies in the midst of hills in the Kandy plateau, which crosses an area of tropical plantations, mainly tea.', '/images/kandy.jpg', 4.7, 2634, 'Central', 'Cultural', 'Year-round', ARRAY['Temple of Tooth', 'Kandy Lake', 'Royal Botanical Gardens', 'Cultural shows'], 7.2906, 80.6337, 10.00, ARRAY['Temple complex', 'Museums', 'Gardens', 'Cultural center']),

('Galle', 'galle', 'Historic Dutch fort city by the Indian Ocean', 'Galle is a major city in Sri Lanka, situated on the southwestern tip of the island. It is the administrative capital of Southern Province and is home to the Galle Fort, a UNESCO World Heritage Site.', '/images/galle.jpg', 4.8, 2198, 'Southern', 'Historical', 'Nov-Apr', ARRAY['Galle Fort', 'Dutch architecture', 'Lighthouse', 'Museums'], 6.0535, 80.2210, 5.00, ARRAY['Fort walls', 'Museums', 'Shops', 'Restaurants']);

-- Insert sample experiences
INSERT INTO experiences (title, slug, description, category, duration, difficulty_level, price_from, includes, requirements, destination_id) VALUES
('Sigiriya Rock Climbing', 'sigiriya-rock-climbing', 'Climb the ancient Lion Rock fortress and explore the royal palace ruins', 'Adventure', '4-5 hours', 'Moderate', 45.00, ARRAY['Entry ticket', 'Professional guide', 'Water bottle'], ARRAY['Good physical fitness', 'Comfortable shoes'], (SELECT id FROM destinations WHERE slug = 'sigiriya')),

('Whale Watching in Mirissa', 'whale-watching-mirissa', 'Experience the thrill of spotting blue whales and dolphins in their natural habitat', 'Wildlife', '3-4 hours', 'Easy', 35.00, ARRAY['Boat ride', 'Life jackets', 'Breakfast'], ARRAY['Early morning departure'], (SELECT id FROM destinations WHERE slug = 'mirissa')),

('Ella Tea Plantation Tour', 'ella-tea-plantation-tour', 'Learn about tea production and enjoy scenic views of the hill country', 'Cultural', '3 hours', 'Easy', 25.00, ARRAY['Factory tour', 'Tea tasting', 'Guide'], ARRAY['Comfortable walking shoes'], (SELECT id FROM destinations WHERE slug = 'ella'));

-- Insert sample itineraries
INSERT INTO itineraries (title, slug, description, duration_days, price, image_url, highlights, best_for, trip_type, includes, excludes) VALUES
('Classic Sri Lanka', 'classic-sri-lanka', 'Experience the best of Sri Lanka in 10 unforgettable days', 10, 1299.00, '/images/classic-tour.jpg', ARRAY['Sigiriya Rock Fortress', 'Kandy Temple', 'Tea Plantations', 'Galle Fort'], ARRAY['First-time visitors', 'Cultural enthusiasts'], 'cultural', ARRAY['Accommodation', 'Transportation', 'Guide', 'Entry fees'], ARRAY['International flights', 'Personal expenses', 'Tips']),

('Beach & Wildlife', 'beach-wildlife', 'Combine pristine beaches with exciting wildlife encounters', 8, 999.00, '/images/beach-wildlife.jpg', ARRAY['Yala National Park', 'Mirissa Beach', 'Whale Watching', 'Udawalawe Safari'], ARRAY['Nature lovers', 'Beach enthusiasts'], 'family', ARRAY['Accommodation', 'Safari jeep', 'Boat trips', 'Meals'], ARRAY['International flights', 'Alcohol', 'Personal expenses']);

-- Insert sample blog posts
INSERT INTO blog_posts (title, slug, excerpt, content, image_url, author_name, author_avatar, category, tags, published, published_at) VALUES
('Hidden Gems of the Hill Country', 'hidden-gems-hill-country', 'Discover secret waterfalls and untouched villages in Sri Lanka''s central highlands...', 'The hill country of Sri Lanka is a treasure trove of hidden gems waiting to be discovered. From secret waterfalls tucked away in lush forests to traditional villages that time forgot, this region offers experiences that go far beyond the typical tourist trail...', '/images/blog/hill-country.jpg', 'Sarah Johnson', '/images/authors/sarah.jpg', 'Travel Tips', ARRAY['Hill Country', 'Hidden Gems', 'Waterfalls'], true, NOW() - INTERVAL '3 days'),

('Street Food Adventures in Colombo', 'street-food-colombo', 'A culinary journey through the bustling streets of Sri Lanka''s capital city...', 'Colombo''s street food scene is a vibrant tapestry of flavors, aromas, and traditions that reflect the island''s rich cultural heritage. From spicy kottu roti to sweet wattalappam, every corner offers a new culinary adventure...', '/images/blog/street-food.jpg', 'Mike Chen', '/images/authors/mike.jpg', 'Food & Culture', ARRAY['Colombo', 'Street Food', 'Culture'], true, NOW() - INTERVAL '5 days');

-- Insert sample reviews
INSERT INTO reviews (destination_id, user_name, user_email, rating, title, content) VALUES
((SELECT id FROM destinations WHERE slug = 'sigiriya'), 'John Smith', 'john@example.com', 5, 'Absolutely breathtaking!', 'The climb was challenging but the views from the top were incredible. The ancient frescoes are remarkably well preserved.'),
((SELECT id FROM destinations WHERE slug = 'mirissa'), 'Emma Wilson', 'emma@example.com', 5, 'Amazing whale watching experience', 'We saw multiple blue whales and dolphins. The boat crew was professional and the experience was unforgettable.'),
((SELECT id FROM destinations WHERE slug = 'ella'), 'David Brown', 'david@example.com', 4, 'Beautiful hill station', 'Great place to relax and enjoy nature. The Nine Arch Bridge is stunning and the tea plantations are beautiful.');

-- Insert sample media gallery
INSERT INTO media_gallery (title, description, image_url, thumbnail_url, category, destination_id, photographer, tags, featured) VALUES
('Sigiriya at Sunrise', 'The ancient rock fortress bathed in golden morning light', '/images/gallery/sigiriya-sunrise.jpg', '/images/gallery/thumbs/sigiriya-sunrise.jpg', 'Landscape', (SELECT id FROM destinations WHERE slug = 'sigiriya'), 'Priya Patel', ARRAY['Sunrise', 'Ancient', 'Landscape'], true),
('Mirissa Beach Sunset', 'Golden hour at one of Sri Lanka''s most beautiful beaches', '/images/gallery/mirissa-sunset.jpg', '/images/gallery/thumbs/mirissa-sunset.jpg', 'Beach', (SELECT id FROM destinations WHERE slug = 'mirissa'), 'Alex Kumar', ARRAY['Sunset', 'Beach', 'Ocean'], true),
('Tea Picker in Ella', 'Traditional tea harvesting in the hill country', '/images/gallery/tea-picker.jpg', '/images/gallery/thumbs/tea-picker.jpg', 'Culture', (SELECT id FROM destinations WHERE slug = 'ella'), 'Sarah Johnson', ARRAY['Tea', 'Culture', 'People'], false);
