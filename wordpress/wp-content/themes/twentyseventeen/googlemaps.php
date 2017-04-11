<?php /* Template Name: Google Maps */ ?>
<?php get_header(); ?>
<?php 
	global $wpdb;
	$result = $wpdb->get_results('SELECT * FROM gm_eq_data',OBJECT);
?>
<div class="wrap">
	<div id="primary" class="content-area">
		<main id="main" class="site-main" role="main">
			<div id="map" style="width: 600px; height: 600px"></div>
		</main>	
	</div>
</div>
<script>
	var map;		
	var results = <?php echo json_encode($result)?>;
	function initMap() {
		map = new google.maps.Map(document.getElementById('map'), {
		center: new google.maps.LatLng(-34.397, 150.644),
		zoom: 2
		});
		var marker, i
		for (i = 0; i<results.length;i++)
		{	
			console.log(results[i]);	
			marker = new google.maps.Marker({
				position: new google.maps.LatLng(results[i].Lat,results[i].Lng),
				title: results[i].Name,
				map: map
			});
			
		}

	}
</script>
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDSCZ5RJiB09E4tpoAcr_wjuf-nw9_eBG0&callback=initMap" async defer></script>

<?php get_footer(); ?>
