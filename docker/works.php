<!DOCTYPE html>
<html>
  <head>
    <title>Browse All Downloaded Works - AO3-DL</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="works.css">
    <link rel="stylesheet" href="custom.css">
    <link rel="icon" href="favicon.png">
  </head>
  <body>
    <div>
      <table>
        <tr>
          <th class="tableColId">ID</th>
          <th class="tableColTitle">Title</th>
          <th class="tableColChapters">Chapters</th>
          <th class="tableColDateDL">Date Downloaded</th>
        </tr>
        <?php
        include("works-inner.php")
        ?>
      </table>
    </div>
  </body>
</html>
