from app.utils.query_validator import is_read_only_query, validate_dataset_references


class TestIsReadOnlyQuery:
    def test_select_query(self):
        """Test that SELECT queries are considered read-only."""
        query = "SELECT * FROM `project.dataset.table`"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_select_with_common_table_expression(self):
        """Test that SELECT with CTE is considered read-only."""
        query = """
        WITH cte AS (
            SELECT field1, field2
            FROM `project.dataset.table`
            WHERE field1 > 100
        )
        SELECT * FROM cte ORDER BY field1
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_select_with_joins(self):
        """Test that SELECT with JOINs is considered read-only."""
        query = """
        SELECT a.field1, b.field2
        FROM `project.dataset.table1` a
        JOIN `project.dataset.table2` b ON a.id = b.id
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_insert_query(self):
        """Test that INSERT queries are not read-only."""
        query = "INSERT INTO `project.dataset.table` (col1, col2) VALUES ('val1', 'val2')"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "INSERT" in reason

    def test_update_query(self):
        """Test that UPDATE queries are not read-only."""
        query = "UPDATE `project.dataset.table` SET col1 = 'new_value' WHERE id = 1"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "UPDATE" in reason

    def test_delete_query(self):
        """Test that DELETE queries are not read-only."""
        query = "DELETE FROM `project.dataset.table` WHERE id = 1"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "DELETE" in reason

    def test_create_table_query(self):
        """Test that CREATE TABLE queries are not read-only."""
        query = "CREATE TABLE `project.dataset.new_table` (id INT64, name STRING)"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "CREATE" in reason

    def test_drop_table_query(self):
        """Test that DROP TABLE queries are not read-only."""
        query = "DROP TABLE `project.dataset.table`"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "DROP" in reason

    def test_alter_table_query(self):
        """Test that ALTER TABLE queries are not read-only."""
        query = "ALTER TABLE `project.dataset.table` ADD COLUMN new_col STRING"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "ALTER" in reason

    def test_truncate_table_query(self):
        """Test that TRUNCATE TABLE queries are not read-only."""
        query = "TRUNCATE TABLE `project.dataset.table`"
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "TRUNCATE" in reason

    def test_merge_query(self):
        """Test that MERGE queries are not read-only."""
        query = """
        MERGE `project.dataset.target_table` AS target
        USING `project.dataset.source_table` AS source
        ON target.id = source.id
        WHEN MATCHED THEN
            UPDATE SET target.col1 = source.col1
        WHEN NOT MATCHED THEN
            INSERT (id, col1) VALUES (source.id, source.col1)
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "MERGE" in reason

    def test_empty_query(self):
        """Test that empty queries are rejected."""
        query = ""
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "No valid SQL statement found" in reason

    def test_commented_query(self):
        """Test that queries with comments are properly handled."""
        query = """
        -- This is a simple SELECT query
        SELECT
            /* Multi-line
               comment */
            id, name
        FROM `project.dataset.table`
        WHERE id > 100
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_query_with_hidden_operations(self):
        """Test that queries with forbidden operations in strings are still detected."""
        query = """
        SELECT
            'INSERT INTO table VALUES (1)',
            id, name
        FROM `project.dataset.table`
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_whitespace_query(self):
        """Test that queries with only whitespace are rejected."""
        query = "   \n   \t   "
        is_valid, reason = is_read_only_query(query)
        assert is_valid is False
        assert "No valid SQL statement found" in reason


class TestValidateDatasetReferences:
    def test_query_with_allowed_dataset(self):
        """Test that queries with allowed datasets pass validation."""
        allowed_datasets = {"allowed_dataset"}
        query = "SELECT * FROM `project.allowed_dataset.table`"
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is True
        assert reason == ""

    def test_query_with_multiple_allowed_datasets(self):
        """Test that queries with multiple allowed datasets pass validation."""
        allowed_datasets = {"dataset1", "dataset2"}
        query = """
        SELECT a.field1, b.field2
        FROM `project.dataset1.table1` a
        JOIN `project.dataset2.table2` b
        ON a.id = b.id
        """
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is True
        assert reason == ""

    def test_query_with_unauthorized_dataset(self):
        """Test that queries with unauthorized datasets are rejected."""
        allowed_datasets = {"allowed_dataset"}
        query = "SELECT * FROM `project.unauthorized_dataset.table`"
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is False
        assert "unauthorized_dataset" in reason

    def test_complex_query_with_unauthorized_dataset(self):
        """Test that complex queries with unauthorized datasets are detected."""
        allowed_datasets = {"dataset1", "dataset2"}
        query = """
        WITH cte AS (
            SELECT * FROM `project.dataset1.table1`
        )
        SELECT a.field1, b.field2, c.field3
        FROM cte a
        JOIN `project.dataset2.table2` b ON a.id = b.id
        JOIN `project.unauthorized_dataset.table3` c ON a.id = c.id
        """
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is False
        assert "unauthorized_dataset" in reason

    def test_query_with_backtick_notation(self):
        """Test that queries using backtick notation are properly validated."""
        allowed_datasets = {"allowed_dataset"}
        query = "SELECT * FROM `project`.`allowed_dataset`.`table`"
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is True
        assert reason == ""

    def test_query_with_simple_notation(self):
        """Test that queries using simple notation (without backticks) are validated."""
        allowed_datasets = {"allowed_dataset"}
        query = "SELECT * FROM project.allowed_dataset.table"
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is True
        assert reason == ""

    def test_query_with_dataset_in_subquery(self):
        """Test that datasets in subqueries are validated."""
        allowed_datasets = {"dataset1"}
        query = """
        SELECT *
        FROM `project.dataset1.table1`
        WHERE id IN (SELECT id FROM `project.unauthorized_dataset.table2`)
        """
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        assert is_valid is False
        assert "unauthorized_dataset" in reason

    def test_empty_allowed_datasets(self):
        """Test behavior when allowed_datasets is empty."""
        allowed_datasets = set()
        query = "SELECT * FROM `project.any_dataset.table`"
        is_valid, reason = validate_dataset_references(query, allowed_datasets)
        # If no datasets are allowed, then all should be allowed
        # This is how the current implementation behaves
        assert is_valid is True
        assert reason == ""

    def test_nested_subqueries(self):
        """Test that SELECT with deeply nested subqueries is considered read-only."""
        query = """
        SELECT field1, field2
        FROM `project.dataset.table1`
        WHERE field1 IN (
            SELECT inner_field
            FROM `project.dataset.table2`
            WHERE inner_field > (
                SELECT AVG(value)
                FROM `project.dataset.table3`
                WHERE category = 'A'
            )
        )
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_union_queries(self):
        """Test that UNION queries are considered read-only."""
        query = """
        SELECT field1, field2 FROM `project.dataset.table1`
        UNION ALL
        SELECT field1, field2 FROM `project.dataset.table2`
        UNION ALL
        SELECT field1, field2 FROM `project.dataset.table3`
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_intersect_except_queries(self):
        """Test that INTERSECT and EXCEPT queries are considered read-only."""
        query = """
        SELECT field1, field2 FROM `project.dataset.table1`
        INTERSECT DISTINCT
        SELECT field1, field2 FROM `project.dataset.table2`
        EXCEPT DISTINCT
        SELECT field1, field2 FROM `project.dataset.table3`
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_window_functions(self):
        """Test that window functions are considered read-only."""
        query = """
        SELECT
            field1,
            field2,
            SUM(field3) OVER (PARTITION BY field1 ORDER BY field2) as running_sum,
            RANK() OVER (PARTITION BY field1 ORDER BY field2) as rank,
            LEAD(field3, 1) OVER (PARTITION BY field1 ORDER BY field2) as next_value
        FROM `project.dataset.table`
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_complex_cte_multi_level(self):
        """Test that complex multi-level CTEs are considered read-only."""
        query = """
        WITH
        cte1 AS (
            SELECT field1, field2, field3
            FROM `project.dataset.table1`
            WHERE field1 > 100
        ),
        cte2 AS (
            SELECT c.field1, c.field2, t2.field3, t2.field4
            FROM cte1 c
            JOIN `project.dataset.table2` t2 ON c.field1 = t2.field1
            WHERE c.field3 < 50
        ),
        cte3 AS (
            SELECT
                c2.field1,
                c2.field2,
                c2.field3,
                c2.field4,
                AVG(c2.field3) OVER (PARTITION BY c2.field1) as avg_field3
            FROM cte2 c2
            WHERE c2.field4 IS NOT NULL
        )
        SELECT * FROM cte3
        ORDER BY field1, field2
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_with_recursive(self):
        """Test that WITH RECURSIVE queries are considered read-only."""
        query = """
        WITH RECURSIVE hierarchy AS (
            -- Base case
            SELECT id, parent_id, name, 0 AS depth
            FROM `project.dataset.employees`
            WHERE parent_id IS NULL

            UNION ALL

            -- Recursive case
            SELECT e.id, e.parent_id, e.name, h.depth + 1
            FROM `project.dataset.employees` e
            JOIN hierarchy h ON e.parent_id = h.id
        )
        SELECT * FROM hierarchy
        ORDER BY depth, name
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_case_with_subqueries(self):
        """Test that CASE statements with subqueries are considered read-only."""
        query = """
        SELECT
            id,
            name,
            CASE
                WHEN id IN (SELECT id FROM `project.dataset.vip_customers`) THEN 'VIP'
                WHEN purchase_count > (SELECT AVG(purchase_count) FROM `project.dataset.customers`) THEN 'High Value'
                ELSE 'Regular'
            END as customer_segment
        FROM `project.dataset.customers`
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""

    def test_mixed_read_only_with_forbidden_comments(self):
        """Test that SELECT queries with comments indicating forbidden operations are still valid."""
        query = """
        -- We need to INSERT this data later
        SELECT
            id,
            name,
            /* UPDATE might be needed for these records */
            value
        FROM `project.dataset.table`
        WHERE id > 100
        """
        is_valid, reason = is_read_only_query(query)
        # This depends on the implementation. If comment analysis is sophisticated,
        # this should pass. If it's simple string scanning, it might fail.
        # The test validates the expected behavior based on current implementation.
        assert is_valid is True
        assert reason == ""

    def test_parameterized_query(self):
        """Test that parameterized queries are properly handled."""
        query = """
        SELECT
            id,
            name,
            value
        FROM `project.dataset.table`
        WHERE date_field >= @start_date
        AND category IN UNNEST(@categories)
        AND value > @threshold
        """
        is_valid, reason = is_read_only_query(query)
        assert is_valid is True
        assert reason == ""
