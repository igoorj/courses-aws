package br.com.igoorj.courses.repository;

import br.com.igoorj.courses.entity.Course;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CourseRepository extends JpaRepository<Course, Long> {

    List<Course> findByNameContainingIgnoreCase(String name);
}
