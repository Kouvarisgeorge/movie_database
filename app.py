# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db
import settings

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        host=settings.mysql_host,
        user=settings.mysql_user,
        password=settings.mysql_passwd,
        database=settings.mysql_schema)

    return con

def updateRank(rank1, rank2, movieTitle):
    try:
        # Μετατρεπουμε τις τιμες σε ακεραιους
        rank1 = int(rank1)
        rank2 = int(rank2)
    except ValueError:
        return [("E","R","R","O","R",)]

    con = connection()

    cur = con.cursor()

    if not (0 <= rank1 <= 10 and 0 <= rank2 <= 10):
        cur.close()
        con.close()
        return [("E","R","R","O","R",)]

    sql = "SELECT a.rank, a.movie_id FROM movie a WHERE a.title = %s"
                
    cur.execute(sql, (movieTitle,))
    
    results = cur.fetchall()

    # Βρεθηκε μια ταινια?
    if len(results) != 1:
        cur.close()
        con.close()
        return [("E","R","R","O","R",)]

    movie_id, current_rank = results[0]  # Παιρνουμε id και τωρινη βαθμολογια

    # Υπολογιχουμε την νεα βαθμολογια
    if current_rank is not None:
        new_rank = (current_rank + rank1 + rank2) / 3
    else:
        new_rank = (rank1 + rank2) / 2

    # Ενημερωνουμε με την νεα βαθμολογια
    update_sql = "UPDATE movie a SET a.rank = %s WHERE a.movie_id = %s"
    cur.execute(update_sql, (new_rank, movie_id))
    con.commit()

    cur.close()
    con.close()
    return [("O","K",)]

  


def colleaguesOfColleagues(a, b):
    
    con = connection()
    cur = con.cursor()
    
    # Ελεγχουμε αν υπαρχουν οι ηθοποιοι
    sql = "SELECT COUNT(*) FROM actor WHERE actor_id = %s"
    cur.execute(sql, (a,))
    result1 = cur.fetchone()[0]
    
    cur.execute(sql, (b,))
    result2 = cur.fetchone()[0]
    
    if result1 == 0 and result2 == 0:
        cur.close()
        con.close()
        return [("I","D","1","","&","","I","D","2","","D","O","E","S","","N","O","T","","E","X","I","S","T",)]
    elif result1 == 0:
        cur.close()
        con.close()
        return [("I","D","1","","D","O","E","S","","N","O","T","","E","X","I","S","T",)]
    elif result2 == 0:
        cur.close()
        con.close()
        return [("I","D","2","","D","O","E","S","","N","O","T","","E","X","I","S","T",)]

    # Βρισκουμε τους συναδελφους του a
    sql_colleagues_a = """
        SELECT DISTINCT r1.actor_id
        FROM role r1
        WHERE r1.movie_id IN (
            SELECT r2.movie_id
            FROM role r2
            WHERE r2.actor_id = %s
        )
        AND r1.actor_id <> %s
    """
    cur.execute(sql_colleagues_a, (a, a))
    colleagues_a = [row[0] for row in cur.fetchall()]

    # Βρισκουμε τους συναδελφους του b
    sql_colleagues_b = """
        SELECT DISTINCT r1.actor_id
        FROM role r1
        WHERE r1.movie_id IN (
            SELECT r2.movie_id
            FROM role r2
            WHERE r2.actor_id = %s
        )
        AND r1.actor_id <> %s
    """
    cur.execute(sql_colleagues_b, (b, b))
    colleagues_b = [row[0] for row in cur.fetchall()]

    combined_results = []
    for colleague_a in colleagues_a:
        for colleague_b in colleagues_b:
            # Ελεγχουμε αν οι ηθοποιοι ειναι διαφορετικοι
            if colleague_a != colleague_b:
                # Βρισκουμε τις κοινες ταινιες του a και b
                sql_movies = """
                    SELECT DISTINCT m.title
                    FROM movie m
                    WHERE m.movie_id IN (
                        SELECT r1.movie_id
                        FROM role r1
                        WHERE r1.actor_id = %s
                    )
                    AND m.movie_id IN (
                        SELECT r2.movie_id
                        FROM role r2
                        WHERE r2.actor_id = %s
                    )
                """
                cur.execute(sql_movies, (colleague_a, colleague_b))
                movies = cur.fetchall()
                for movie in movies:
                    combined_results.append((movie[0], colleague_a, colleague_b, a, b))

    cur.close()
    con.close()

    # Φτιαχνουμε την λιστα αποτελεσματων
    result_list = [("movieTitle", "colleagueOfActor1", "colleagueofActor2", "actor1", "actor2")]
    for row in combined_results:
        result_list.append((row[0], row[1], row[2], row[3], row[4]))

    return result_list







def actorPairs(actorId):
    
    con = connection()
    cur = con.cursor()
    
    # Ελεγχος αν υπαρχει ο ηθοποιος
    sql = "SELECT COUNT(*) FROM actor WHERE actor_id = %s"
    cur.execute(sql, (actorId,))
    result1 = cur.fetchone()[0]
    
    if result1 == 0:
        cur.close()
        con.close()
        return [("D", "O", "E", "S", "N", "O", "T", "E", "X", "I", "S", "T")]

    # Ανακτηση των ειδων στα οποια εχει παιξει ο συγκεκριμενος ηθοποιος
    genre_query = """
    SELECT DISTINCT mhg.genre_id
    FROM movie_has_genre mhg
    WHERE mhg.movie_id IN (
        SELECT r.movie_id
        FROM role r
        WHERE r.actor_id = %s
    )
    """
    cur.execute(genre_query, (actorId,))
    actor_genres = cur.fetchall()
    actor_genres = [g[0] for g in actor_genres]

    #Αν δεν εχει ειδη
    if not actor_genres:
        cur.close()
        con.close()
        return [("N", "O", "R", "E", "S", "U", "L", "T", "S")]

    # Βρισκουμε ολα τα ζευγη ηθοποιων που εχουν παιξει σε τουλαχιστον επτα διαφορετικα ειδη μαζι
    actor_pairs_query = """
    SELECT DISTINCT r2.actor_id
    FROM role r1, role r2, movie_has_genre mhg
    WHERE r1.movie_id = r2.movie_id
      AND r1.movie_id = mhg.movie_id
      AND r1.actor_id < r2.actor_id
      AND r1.actor_id = %s
      AND r2.actor_id != %s
      AND NOT EXISTS (
          SELECT 1
          FROM movie_has_genre mhg2
          WHERE mhg2.movie_id IN (
              SELECT r3.movie_id
              FROM role r3
              WHERE r3.actor_id = r2.actor_id
          )
          AND mhg2.genre_id IN (%s)
      )
    GROUP BY r2.actor_id
    HAVING COUNT(DISTINCT mhg.genre_id) >= 7
    """
    formatted_actor_genres = ', '.join(str(genre) for genre in actor_genres)
    cur.execute(actor_pairs_query, (actorId, actorId, formatted_actor_genres))
    results = cur.fetchall()

    cur.close()
    con.close()

    # Ελεγχος αν υπαρχουν αποτελεσματα
    if not results:
        return [("E", "R", "R", "O", "R")]

    # Επιστροφη των κωδικων των ηθοποιων
    result_list = [("actor_id",)]
    for result in results:
        result_list.append(result)

    return result_list

        

def selectTopNactors(n):
    
    con = connection()
    cur = con.cursor()
    
    #Κανουμε ακεραιο το ορισμα
    try:
        n=int(n)
    except ValueError:
        return [("E","R","R","O","R",)]

    sql= """
        SELECT genre_name, actor_id, movie_count
        FROM (
            SELECT DISTINCT g.genre_name, a.actor_id, COUNT(r.movie_id) AS movie_count,
            ROW_NUMBER() OVER (PARTITION BY g.genre_name ORDER BY COUNT(r.movie_id) DESC) AS row_num
            FROM actor a, genre g, role r, movie_has_genre mhg
            WHERE a.actor_id = r.actor_id
            AND r.movie_id = mhg.movie_id
            AND mhg.genre_id = g.genre_id
            GROUP BY g.genre_name, a.actor_id
            HAVING movie_count > 0
        ) AS top_actors
        WHERE row_num <= %s
        ORDER BY genre_name, movie_count DESC;
    """

    cur.execute(sql, (n,))
    top_actors = cur.fetchall()

    cur.close()
    con.close()
    
    result_list = [("genre_name", "actor_id", "movie_count")]

    # Προσθηκη των κορυφαιων Ν ηθοποιων στη λιστα αποτελεσματων
    for row in top_actors:
        result_list.append(row)
        
    return result_list





def traceActorInfluence(actorId):
    con = connection()
    cur = con.cursor()

    # Βρισκουμε τις αμεσες επιρροες
    direct_influences_query = """
    SELECT DISTINCT r2.actor_id
    FROM role r1, role r2, movie m1, movie m2, movie_has_genre mhg1, movie_has_genre mhg2
    WHERE r1.movie_id = m1.movie_id
      AND r2.movie_id = m2.movie_id
      AND m1.movie_id = mhg1.movie_id
      AND m2.movie_id = mhg2.movie_id
      AND r1.actor_id = %s
      AND r1.actor_id != r2.actor_id
      AND mhg1.genre_id = mhg2.genre_id
      AND m1.year < m2.year
    """
    cur.execute(direct_influences_query, (actorId,))
    direct_influences = cur.fetchall()
    influenced_actors = set([actor[0] for actor in direct_influences])

    # Αρχικοποιουμε το συνολο των επιρροων
    all_influences = set(influenced_actors)

    # Ευρεση εμμεσων επιρροων
    while direct_influences:
        new_influences = set()
        for actor in direct_influences:
            cur.execute(direct_influences_query, (actor,))
            indirect_influences = cur.fetchall()
            for indirect in indirect_influences:
                if indirect[0] not in all_influences:
                    new_influences.add(indirect[0])
                    all_influences.add(indirect[0])
        direct_influences = list(new_influences)

    cur.close()
    con.close()

    # φτιαχνουμε μια λιστα για τα αποτελεσματα
    result_list = [("influencedActorId",)]
    for actor in all_influences:
        result_list.append((actor,))

    return result_list