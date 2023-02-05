<?php
session_name("wsgame");
session_start();
session_destroy();
header("Location: index.php");
?>