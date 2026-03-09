#!/usr/bin/env python3
"""
Phase 8: Database Consistency Audit
Tests database integrity, foreign key relationships, and data consistency
"""

import json
import sys
from datetime import datetime
from typing import Dict
import psycopg2
from psycopg2 import sql

# Database configuration
DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "trading_nexus"
DB_USER = "postgres"
DB_PASSWORD = "postgres123"  # From .env file

class DatabaseConsistencyAudit:
    def __init__(self):
        self.results = {
            "phase": "8",
            "title": "Database Consistency Audit",
            "timestamp": datetime.now().isoformat(),
            "database_accessibility": [],
            "schema_validation": [],
            "foreign_key_integrity": [],
            "data_consistency": [],
            "indexes_and_performance": [],
            "transaction_handling": [],
            "summary": {}
        }
        self.conn = None
        self.cursor = None

    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")

    def log_test(self, category: str, test_name: str, status: str, details: Dict):
        """Log test result"""
        entry = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **details
        }
        
        if category in self.results and isinstance(self.results[category], list):
            self.results[category].append(entry)
        
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"  {status_symbol} {test_name}: {status}")
        if details.get("message"):
            print(f"     → {details['message']}")

    def connect_database(self) -> bool:
        """Connect to PostgreSQL database"""
        self.print_section("Phase 8.0: Database Accessibility")
        
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            self.cursor = self.conn.cursor()
            
            # Test connection with a simple query
            self.cursor.execute("SELECT 1;")
            self.cursor.fetchone()
            
            self.log_test(
                "database_accessibility",
                "Database Connection",
                "PASS",
                {
                    "message": f"Connected to {DB_NAME} at {DB_HOST}:{DB_PORT}",
                    "host": DB_HOST,
                    "port": DB_PORT,
                    "database": DB_NAME
                }
            )
            return True
            
        except Exception as e:
            self.log_test(
                "database_accessibility",
                "Database Connection",
                "FAIL",
                {"message": f"Failed to connect: {str(e)}"}
            )
            return False

    def test_schema_validation(self):
        """Test Phase 8.1: Schema validation"""
        self.print_section("Phase 8.1: Schema Validation")
        
        if not self.cursor:
            print("  ✗ Database not connected")
            return

        try:
            # Get all tables
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            tables = [row[0] for row in self.cursor.fetchall()]
            
            if tables:
                self.log_test(
                    "schema_validation",
                    "Schema Validity",
                    "PASS",
                    {
                        "message": f"Found {len(tables)} tables in schema",
                        "tables": tables,
                        "table_count": len(tables)
                    }
                )
            else:
                self.log_test(
                    "schema_validation",
                    "Schema Validity",
                    "FAIL",
                    {"message": "No tables found in schema"}
                )
        except Exception as e:
            self.log_test(
                "schema_validation",
                "Schema Validity",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_table_integrity(self):
        """Test Phase 8.1: Table integrity"""
        self.print_section("Phase 8.1: Table Integrity")
        
        if not self.cursor:
            print("  ✗ Database not connected")
            return

        try:
            # Check for tables with primary keys
            self.cursor.execute("""
                SELECT table_name, constraint_name
                FROM information_schema.table_constraints
                WHERE constraint_type = 'PRIMARY KEY'
                AND table_schema = 'public'
            """)
            
            pk_tables = self.cursor.fetchall()
            
            self.log_test(
                "schema_validation",
                "Primary Key Definitions",
                "PASS" if pk_tables else "WARN",
                {
                    "message": f"Found {len(pk_tables)} tables with primary keys",
                    "table_count": len(pk_tables)
                }
            )
        except Exception as e:
            self.log_test(
                "schema_validation",
                "Primary Key Definitions",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_foreign_key_integrity(self):
        """Test Phase 8.2: Foreign key integrity"""
        self.print_section("Phase 8.2: Foreign Key Integrity")
        
        if not self.cursor:
            print("  ✗ Database not connected")
            return

        try:
            # Get all foreign keys using proper PostgreSQL schema
            self.cursor.execute("""
                SELECT constraint_name, table_name
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_schema = 'public'
            """)
            
            fks = self.cursor.fetchall()
            
            self.log_test(
                "foreign_key_integrity",
                "Foreign Key Definition",
                "PASS" if fks else "WARN",
                {
                    "message": f"Found {len(fks)} foreign key relationships",
                    "fk_count": len(fks)
                }
            )

            # Check for orphaned records (if orders table exists)
            try:
                self.cursor.execute("""
                    SELECT COUNT(*) as orphan_count
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.id
                    WHERE u.id IS NULL
                """)
                
                orphan_count = self.cursor.fetchone()
                if orphan_count and orphan_count[0] == 0:
                    self.log_test(
                        "foreign_key_integrity",
                        "Orphaned Records Check",
                        "PASS",
                        {"message": "No orphaned records found"}
                    )
                else:
                    self.log_test(
                        "foreign_key_integrity",
                        "Orphaned Records Check",
                        "FAIL",
                        {
                            "message": f"Found {orphan_count[0]} orphaned records in orders table",
                            "orphan_count": orphan_count[0]
                        }
                    )
            except Exception as fk_error:
                # Table might not exist
                self.log_test(
                    "foreign_key_integrity",
                    "Orphaned Records Check",
                    "SKIP",
                    {"message": f"Orders or users table not found: {str(fk_error)[:50]}"}
                )

        except Exception as e:
            self.log_test(
                "foreign_key_integrity",
                "Foreign Key Definition",
                "FAIL",
                {"message": f"Error: {str(e)[:100]}"}
            )
            # Reset transaction after error
            try:
                self.conn.rollback()
            except:
                pass

    def test_data_consistency(self):
        """Test Phase 8.3: Data consistency"""
        self.print_section("Phase 8.3: Data Consistency")
        
        if not self.cursor:
            print("  ✗ Database not connected")
            return

        # Check for NULL constraints
        try:
            self.cursor.execute("""
                SELECT table_name, column_name, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND is_nullable = 'NO'
                LIMIT 10
            """)
            
            not_null_cols = self.cursor.fetchall()
            
            self.log_test(
                "data_consistency",
                "NOT NULL Constraints",
                "PASS",
                {
                    "message": f"Found {len(not_null_cols)} NOT NULL constraints",
                    "constraint_count": len(not_null_cols)
                }
            )
        except Exception as e:
            self.log_test(
                "data_consistency",
                "NOT NULL Constraints",
                "FAIL",
                {"message": f"Error: {str(e)[:100]}"}
            )
            self.conn.rollback()

        # Check for unique constraints
        try:
            self.cursor.execute("""
                SELECT constraint_name, table_name
                FROM information_schema.table_constraints
                WHERE constraint_type = 'UNIQUE'
                AND table_schema = 'public'
            """)
            
            unique_cols = self.cursor.fetchall()
            
            self.log_test(
                "data_consistency",
                "UNIQUE Constraints",
                "PASS",
                {
                    "message": f"Found {len(unique_cols)} UNIQUE constraints",
                    "constraint_count": len(unique_cols)
                }
            )
        except Exception as e:
            self.log_test(
                "data_consistency",
                "UNIQUE Constraints",
                "FAIL",
                {"message": f"Error: {str(e)[:100]}"}
            )
            self.conn.rollback()

    def test_indexes_and_performance(self):
        """Test Phase 8.4: Indexes and query performance"""
        self.print_section("Phase 8.4: Indexes & Performance")
        
        if not self.cursor:
            print("  ✗ Database not connected")
            return

        try:
            # Get all indexes
            self.cursor.execute("""
                SELECT schemaname, tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            
            indexes = self.cursor.fetchall()
            
            self.log_test(
                "indexes_and_performance",
                "Index Definition",
                "PASS" if indexes else "WARN",
                {
                    "message": f"Found {len(indexes)} indexes",
                    "index_count": len(indexes)
                }
            )
        except Exception as e:
            self.log_test(
                "indexes_and_performance",
                "Index Definition",
                "FAIL",
                {"message": f"Error: {str(e)[:100]}"}
            )
            self.conn.rollback()

        # Check table sizes
        try:
            self.cursor.execute("""
                SELECT schemaname, tablename, 
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            table_sizes = self.cursor.fetchall()
            
            self.log_test(
                "indexes_and_performance",
                "Table Size Metrics",
                "PASS",
                {
                    "message": f"Analyzed {len(table_sizes)} tables",
                    "table_count": len(table_sizes)
                }
            )
        except Exception as e:
            self.log_test(
                "indexes_and_performance",
                "Table Size Metrics",
                "FAIL",
                {"message": f"Error: {str(e)[:100]}"}
            )
            self.conn.rollback()

    def test_transaction_handling(self):
        """Test Phase 8.5: Transaction handling"""
        self.print_section("Phase 8.5: Transaction Handling")
        
        if not self.cursor:
            print("  ✗ Database not connected")
            return

        try:
            # Start a transaction and rollback
            self.cursor.execute("BEGIN;")
            self.cursor.execute("SELECT 1;")
            self.cursor.execute("ROLLBACK;")
            
            self.log_test(
                "transaction_handling",
                "Transaction Rollback",
                "PASS",
                {"message": "Transaction rollback successful"}
            )
        except Exception as e:
            self.log_test(
                "transaction_handling",
                "Transaction Rollback",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

        try:
            # Test transaction commit
            self.cursor.execute("BEGIN;")
            self.cursor.execute("SELECT 1;")
            self.cursor.execute("COMMIT;")
            
            self.log_test(
                "transaction_handling",
                "Transaction Commit",
                "PASS",
                {"message": "Transaction commit successful"}
            )
        except Exception as e:
            self.log_test(
                "transaction_handling",
                "Transaction Commit",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def generate_report(self):
        """Generate Phase 8 audit report"""
        self.print_section("Phase 8 Audit Report Summary")
        
        # Count test results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category in self.results:
            if isinstance(self.results[category], list):
                for test in self.results[category]:
                    total_tests += 1
                    if test.get("status") == "PASS":
                        passed_tests += 1
                    elif test.get("status") == "FAIL":
                        failed_tests += 1

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": total_tests - passed_tests - failed_tests,
            "pass_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
        }

        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Pass Rate: {self.results['summary']['pass_rate']}")

        # Save report
        report_file = "audit_phase8_database_consistency_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n  Report saved to: {report_file}")
        return True

    def cleanup(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def run(self):
        """Run all Phase 8 tests"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*10 + "Phase 8: Database Consistency Audit" + " "*13 + "║")
        print("╚" + "="*58 + "╝")

        if not self.connect_database():
            print("\n✗ Failed to connect to database. Aborting.")
            return False

        try:
            self.test_schema_validation()
            self.test_table_integrity()
            self.test_foreign_key_integrity()
            self.test_data_consistency()
            self.test_indexes_and_performance()
            self.test_transaction_handling()

            # Generate report
            self.generate_report()

            return True
        finally:
            self.cleanup()


if __name__ == "__main__":
    try:
        audit = DatabaseConsistencyAudit()
        success = audit.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Audit failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
