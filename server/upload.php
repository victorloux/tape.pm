<?php
/**
 * This file receives an upload (file sent from the art installation),
 * checks it and if it is correct, stores it in a folder. It returns
 * correct response codes usable by the Python scripts on the installation
 *
 * In the future it could be expanded to store additional data in a database
 *
 * (c) 2016 Victor Loux / b00t consultants ltd
 */

// @todo: log everything in a separate file

// ini_set('display_errors', 1);
// error_reporting(E_ALL);

const UPLOAD_KEY = '[your-upload-key-here]';
const UPLOAD_FOLDER = "uploads/";
const ALLOWABLE_EXTENSION = "mp3";

// Determine the max upload size (whichever value is lowest)
$max_upload      = (int)(ini_get('upload_max_filesize'));
$max_post        = (int)(ini_get('post_max_size'));
$memory_limit    = (int)(ini_get('memory_limit'));
$max_upload_size = min($max_upload, $max_post, $memory_limit);

// Compare the upload key
// @todo: if it doesn't work try _GET
if($_POST['upload_key'] !== UPLOAD_KEY) {
	http_response_code(403);
	die("Forbidden");
}

// Check for upload errors
if ($_FILES['soundfile']['error'] === UPLOAD_ERR_NO_FILE) {
	http_response_code(405);
    die('No file sent');
}

// Max filesize
if (($_FILES['soundfile']['size'] / 1024 / 1024) > $max_upload_size || $_FILES['soundfile']['error'] === UPLOAD_ERR_INI_SIZE || $_FILES['soundfile']['error'] === UPLOAD_ERR_FORM_SIZE) {
	http_response_code(405);
    print_r($_FILES['soundfile']['size']); echo " --- \n";
    print_r($max_upload_size); echo " --- \n";
    die('Exceeded filesize limit');
}

// Any other error
if ($_FILES['soundfile']['error'] !== UPLOAD_ERR_OK) {
	http_response_code(405);
    die('Unknown error');
}

// Check extension
// @todo: also check MIME == audio/x-wav?

// $tmp = new SplFileInfo($_FILES['soundfile']['tmp_name']);

// if($tmp->getExtension() !== ALLOWABLE_EXTENSION) {
//	http_response_code(403);
//	print_r($tmp);
//	var_dump($tmp->getExtension());
//	die("Forbidden");
// }


// Try to move it & upload it
$destination = UPLOAD_FOLDER . basename($_FILES['soundfile']['name']);

if(move_uploaded_file($_FILES['soundfile']['tmp_name'], $destination)) {
	http_response_code(200);
	echo "OK";
}
else {
	http_response_code(405);
	echo "File could not be moved, check permissions";
}
