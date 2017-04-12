<?php /* Template Name: Google Maps */ ?>
<?php get_header(); ?>
<?php 
	global $wpdb;

	// get default values
	//
	//
	$start_date = $wpdb->get_var("SELECT * FROM gm_eq_data ORDER BY Time ASC LIMIT 1;",6,0);
	$start_date = substr($start_date, 0, strrpos($start_date,' '));
	$end_date = $wpdb->get_var("SELECT * FROM gm_eq_data ORDER BY Time DESC LIMIT 1;",6,0);
	$end_date = substr($end_date, 0, strrpos($end_date, ' ')); 
	$mag = -1.0;	
	if (isset($_GET['startdate']))
	{
		$start_date = $_GET['startdate'];
	}
	if (isset($_GET['enddate']))
	{
		$end_date = $_GET['enddate'];
	}
	if (isset($_GET['mag']))
	{
		$mag = $_GET['mag'];
	}
	$result = $wpdb->get_results($wpdb->prepare("SELECT * FROM gm_eq_data WHERE Time>=%s AND Time<=%s AND Mag>=%s",array($start_date,$end_date,$mag)), OBJECT);

	
	
?>

<div class="wrap">
	<div id="primary" class="content-area">
		<main id="main" class="site-main" role="main">
			<div id="input_form">
				<form action="/index.php/google-map/">
					Start Date:
					<input type="date" name="startdate" value="<?php echo $start_date?>" min="2017-03-01">
					End Date:
					<input type="date" name="enddate" value="<?php echo $end_date?>">
					Magnitude higher than: 
					<input type="number" name="mag" value="<?php echo $mag?>" step="0.01">
					<input type="submit">
				</form>
			</div>
			<div id="map" style="margin-top: 5%; height: 600px"></div>	
		</main>	
	</div>
</div>
<script>
	var map;		
	var results = <?php echo json_encode($result)?>;
	function initMap() {
		map = new google.maps.Map(document.getElementById('map'), {
		center: new google.maps.LatLng(0, 0),
		zoom: 2
		});
		var marker, i
		for (i = 0; i<results.length;i++)
		{	
			console.log(results[i]);	
			marker = new google.maps.Marker({
				position: new google.maps.LatLng(results[i].Lat,results[i].Lng),
				title: results[i].Place,
				map: map
			});
			
		}

	}
</script>
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDSCZ5RJiB09E4tpoAcr_wjuf-nw9_eBG0&callback=initMap" async defer></script>

<?php get_footer(); ?>
