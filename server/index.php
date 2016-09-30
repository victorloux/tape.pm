<?php
// ini_set('display_errors', 'On');
// error_reporting(E_ALL);

const UPLOAD_FOLDER = "uploads/";
// const BASE = 'http://tape.pm';
const BASE = 'http://localhost/tapepm';

$hashid = '';
$location = '';

// if we're using the form, use the correct URI
if(isset($_POST['id'])) {
	header("Location: /" . $_POST['id']);
	exit;
}

// sanitize: do not allow any character that can't be in the hashid (a-z 0-9)
// strtolower it first in case people do use uppercase
if(isset($_GET['id'])) {
	$hashid = mb_ereg_replace('[^abcdefghjkmnpqrtuvwxyz02346789]+', '', strtolower($_GET['id']));
	$location = UPLOAD_FOLDER . $hashid . '.mp3';
	if(!file_exists($location)) {
		$location = '';
	}
}

// Force download if we go to /download
if(isset($_GET['download']) && $_GET['download'] == 1) {
	if(!empty($location)) {
		$size   = filesize($location);

		header('Content-Description: File Transfer');
		header('Content-Type: application/octet-stream');
		header('Content-Disposition: attachment; filename=tapepm-' . $hashid . '.mp3');
		header('Content-Transfer-Encoding: binary');
		header('Connection: Keep-Alive');
		header('Expires: 0');
		header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
		header('Pragma: public');
		header('Content-Length: ' . $size);
		readfile($location);
		exit;
	}
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="<?php echo BASE; ?>/style.css">

	<link rel="stylesheet" type="text/css" href="<?php echo BASE; ?>/script/360player.css" />
	<link rel="stylesheet" type="text/css" href="<?php echo BASE; ?>/script/360player-visualization.css" />

	<?php if(empty($location)): ?>
		<title>tape.pm</title>
	<?php else: ?>
		<title>tape.pm / recording <?php echo $hashid; ?></title>
	<?php endif; ?>
</head>
<body>
	<div id="container">
		<?php if(empty($location) || !isset($_GET['id'])): ?>
			<h1>tape.p<span>rint</span>m<span>achine</span></h1>

			<?php if(empty($location) && !empty($hashid)): ?>
				<div class="error">Code not found! Check your code is correct.</div>
			<?php endif; ?>

			<form action="." method="POST">
				<label>Your code: <input type="text" name="id" id="code" value="<?php echo $hashid; ?>"></label>
				<input type="submit" value="OK">
			</form>
		<?php else: ?>
			<h1>tape.p<span>rint</span>m<span>achine</span><span class="code">/<?php echo $hashid; ?></span></h1>

			<div style="clear:both"></div>

			<div class="audio">
				<div class="ui360 ui360-vis"><a href="<?php echo BASE . '/' . $location; ?>"> - </a></div>
			</div>

			<h4><span class="record">&bull;</span> Recorded on <?php echo date("d/m/Y H:i", filectime($location)); ?> </h4>
			<ul class="share">
				<li><a href="/<?php echo $hashid ?>/download" class="shr-dl">download a mp3</a></li>
				<li><a href="https://twitter.com/home?status=I+played+with+@CollidoscopeLab+and+I+made+something+amazing.+<?php echo BASE . '/' . $hashid ?>" class="shr-tweet">tweet it</a></li>
				<li><a href="https://www.facebook.com/sharer/sharer.php?u=<?php echo BASE . '/' . $hashid ?>" class="shr-fb">facebook it</a></li>
			</ul>
		<?php endif; ?>

		<div class="sub">
			&copy; 2016 b00t &mdash;
			<!-- privacy policy &mdash; -->
			<a href="http://collidoscope.io">collidoscope</a>
		</div>
	</div>

	<script type="text/javascript" src="<?php echo BASE; ?>/script/berniecode-animator.js"></script>
	<script type="text/javascript" src="<?php echo BASE; ?>/script/soundmanager2-nodebug-jsmin.js"></script>
	<script type="text/javascript" src="<?php echo BASE; ?>/script/360player.js"></script>

	<script>
soundManager.setup({
  // path to directory containing SM2 SWF
  url: '/script/swf/'
});

threeSixtyPlayer.config.scaleFont = (navigator.userAgent.match(/msie/i)?false:true);
threeSixtyPlayer.config.showHMSTime = true;

// enable some spectrum stuffs

threeSixtyPlayer.config.useWaveformData = true;
threeSixtyPlayer.config.useEQData = true;

// enable this in SM2 as well, as needed

if (threeSixtyPlayer.config.useWaveformData) {
  soundManager.flash9Options.useWaveformData = true;
}
if (threeSixtyPlayer.config.useEQData) {
  soundManager.flash9Options.useEQData = true;
}
if (threeSixtyPlayer.config.usePeakData) {
  soundManager.flash9Options.usePeakData = true;
}

if (threeSixtyPlayer.config.useWaveformData || threeSixtyPlayer.flash9Options.useEQData || threeSixtyPlayer.flash9Options.usePeakData) {
  // even if HTML5 supports MP3, prefer flash so the visualization features can be used.
  soundManager.preferFlash = true;
}


</script>
</body>
</html>