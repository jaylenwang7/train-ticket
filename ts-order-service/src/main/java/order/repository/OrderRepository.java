package order.repository;

import order.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * @author fdse
 */
@Repository
public interface OrderRepository extends JpaRepository<Order, String> {

    @Override
    Optional<Order> findById(String id);

    @Override
    ArrayList<Order> findAll();

    ArrayList<Order> findByAccountId(String accountId);

    ArrayList<Order> findByTravelDateAndTrainNumber(String travelDate,String trainNumber);

    @Override
    void deleteById(String id);
    
    ArrayList<Order> findByAccountIdAndStatus(String accountId, int status);
    
    ArrayList<Order> findByAccountIdAndBoughtDateBetween(String accountId, String boughtDateStart, String boughtDateEnd);
    
    ArrayList<Order> findByAccountIdAndTravelDateBetween(String accountId, String travelDateStart, String travelDateEnd);
    
    @Query("SELECT o FROM Order o WHERE o.accountId = :accountId AND " +
           "(:enableStateQuery = false OR o.status = :state) AND " +
           "(:enableBoughtDateQuery = false OR (o.boughtDate >= :boughtDateStart AND o.boughtDate <= :boughtDateEnd)) AND " +
           "(:enableTravelDateQuery = false OR (o.travelDate >= :travelDateStart AND o.travelDate <= :travelDateEnd))")
    ArrayList<Order> findByAccountIdWithFilters(
            @Param("accountId") String accountId,
            @Param("enableStateQuery") boolean enableStateQuery,
            @Param("state") int state,
            @Param("enableBoughtDateQuery") boolean enableBoughtDateQuery,
            @Param("boughtDateStart") String boughtDateStart,
            @Param("boughtDateEnd") String boughtDateEnd,
            @Param("enableTravelDateQuery") boolean enableTravelDateQuery,
            @Param("travelDateStart") String travelDateStart,
            @Param("travelDateEnd") String travelDateEnd);
    
    @Query("SELECT COUNT(o) FROM Order o WHERE o.accountId = :accountId AND o.boughtDate >= :dateFrom")
    int countOrdersInLastHour(@Param("accountId") String accountId, @Param("dateFrom") String dateFrom);
    
    @Query("SELECT COUNT(o) FROM Order o WHERE o.accountId = :accountId AND o.status IN :validStatuses")
    int countValidOrders(@Param("accountId") String accountId, @Param("validStatuses") List<Integer> validStatuses);
}
